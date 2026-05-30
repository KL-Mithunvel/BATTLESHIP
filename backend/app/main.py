import asyncio
import json
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, ValidationError

from .api import health_routes, lobby_routes, game_routes
from .game.board import Board
from .game.rules import validate_placements, build_ships
from .game.ship import SHIP_TYPES
from .server.events import (
    EVT_PLACE_SHIPS, EVT_PLAYER_READY, EVT_FIRE,
    EVT_ROOM_JOINED, EVT_OPPONENT_JOINED, EVT_PLACEMENT_PHASE,
    EVT_PLACEMENT_CONFIRMED, EVT_GAME_START, EVT_SHOT_RESULT,
    EVT_YOUR_TURN, EVT_GAME_OVER, EVT_OPPONENT_DISCONNECTED, EVT_ERROR,
)
from .server.lobby import LobbyStatus
from .server.lobby_manager import lobby_manager
from .server.websocket_manager import ws_manager

# ---------------------------------------------------------------------------
# Pydantic models for WebSocket message validation (DR-2)
# ---------------------------------------------------------------------------

class PlacementItem(BaseModel):
    name: str
    row: int
    col: int
    horizontal: bool

    @field_validator("name")
    @classmethod
    def valid_ship(cls, v: str) -> str:
        if v not in SHIP_TYPES:
            raise ValueError(f"Unknown ship: {v}")
        return v

    @field_validator("row", "col")
    @classmethod
    def in_bounds(cls, v: int) -> int:
        if not (0 <= v <= 9):
            raise ValueError("Coordinate must be 0–9")
        return v


class PlaceShipsMsg(BaseModel):
    placements: list[PlacementItem]


class FireMsg(BaseModel):
    row: int
    col: int

    @field_validator("row", "col")
    @classmethod
    def in_bounds(cls, v: int) -> int:
        if not (0 <= v <= 9):
            raise ValueError("Coordinate must be 0–9")
        return v


class IncomingMsg(BaseModel):
    event: str
    data: dict = {}


# ---------------------------------------------------------------------------
# App + middleware
# ---------------------------------------------------------------------------

# DR-7: CORS origins from environment variable, never wildcard in production
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",")]

app = FastAPI(title="Battleship API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_routes.router)
app.include_router(lobby_routes.router)
app.include_router(game_routes.router)


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

@app.websocket("/ws/{lobby_code}/{player_id}")
async def ws_endpoint(ws: WebSocket, lobby_code: str, player_id: str) -> None:
    lobby_code = lobby_code.upper()
    lobby = lobby_manager.get(lobby_code)

    # DR-6: reject any connection that cannot be matched to a lobby player
    if not lobby or player_id not in lobby.players:
        await ws.close(code=4001)
        return

    await ws_manager.connect(player_id, ws)
    player_ids = lobby.player_ids()
    opponent_id = next((pid for pid in player_ids if pid != player_id), None)

    await ws_manager.send(player_id, EVT_ROOM_JOINED, {
        "lobby_code": lobby_code,
        "player_id": player_id,
        "username": lobby.players[player_id].username,
    })

    # If both players are now connected, sync game state
    if opponent_id and ws_manager.is_connected(opponent_id):
        my_name = lobby.players[player_id].username
        opp_name = lobby.players[opponent_id].username
        await ws_manager.send(player_id, EVT_OPPONENT_JOINED, {"username": opp_name})
        await ws_manager.send(opponent_id, EVT_OPPONENT_JOINED, {"username": my_name})

        if lobby.status == LobbyStatus.PLAYERS_JOINED:
            lobby_manager.start_placement(lobby_code)
            await ws_manager.broadcast(player_ids, EVT_PLACEMENT_PHASE, {})
        elif lobby.status == LobbyStatus.SHIP_PLACEMENT:
            # Reconnect during placement — resync the reconnecting player
            await ws_manager.send(player_id, EVT_PLACEMENT_PHASE, {})
        elif lobby.status == LobbyStatus.IN_PROGRESS and lobby.engine:
            # Reconnect mid-game — resync current state
            await ws_manager.send(player_id, EVT_GAME_START, {
                "first_turn": lobby.engine.state.current_turn,
                "players": {pid: lobby.players[pid].username for pid in player_ids},
            })
            if lobby.engine.state.current_turn == player_id:
                await ws_manager.send(player_id, EVT_YOUR_TURN, {})

    try:
        while True:
            raw = await ws.receive_text()

            # DR-2: validate message structure before acting on it
            try:
                msg = IncomingMsg.model_validate_json(raw)
            except (ValidationError, ValueError):
                await ws_manager.send(player_id, EVT_ERROR, {"message": "Invalid message format"})
                continue

            # DR-8: catch handler errors so one bad message cannot crash the connection
            try:
                if msg.event == EVT_PLACE_SHIPS:
                    await _handle_place_ships(lobby_code, player_id, msg.data)
                elif msg.event == EVT_PLAYER_READY:
                    await _handle_ready(lobby_code, player_id)
                elif msg.event == EVT_FIRE:
                    await _handle_fire(lobby_code, player_id, msg.data)
                # Unknown events are silently ignored
            except Exception:
                await ws_manager.send(player_id, EVT_ERROR, {"message": "An error occurred"})

    except WebSocketDisconnect:
        ws_manager.disconnect(player_id)
        if opponent_id and ws_manager.is_connected(opponent_id):
            # Short grace period: lets the client reconnect before we declare them gone.
            # This prevents React StrictMode's cleanup+remount cycle from falsely
            # triggering opponent_disconnected during development.
            await asyncio.sleep(0.5)
            if not ws_manager.is_connected(player_id):
                await ws_manager.send(opponent_id, EVT_OPPONENT_DISCONNECTED, {})


# ---------------------------------------------------------------------------
# WS message handlers
# ---------------------------------------------------------------------------

async def _handle_place_ships(lobby_code: str, player_id: str, data: dict) -> None:
    try:
        msg = PlaceShipsMsg.model_validate(data)
    except ValidationError:
        await ws_manager.send(player_id, EVT_ERROR, {"message": "Invalid placement data"})
        return

    placements_dicts = [p.model_dump() for p in msg.placements]
    valid, reason = validate_placements(placements_dicts)
    if not valid:
        await ws_manager.send(player_id, EVT_ERROR, {"message": reason})
        return

    lobby = lobby_manager.get(lobby_code)
    if not lobby:
        return

    player = lobby.players[player_id]
    player.board = Board()  # reset board so re-placement is allowed before ready

    ships = build_ships(placements_dicts)
    for placement, ship in zip(msg.placements, ships):
        ok = player.board.place_ship(ship, placement.row, placement.col, placement.horizontal)
        if not ok:
            player.board = Board()
            await ws_manager.send(player_id, EVT_ERROR, {"message": f"Invalid placement for {ship.name}"})
            return

    player.ships_placed = True
    await ws_manager.send(player_id, EVT_PLACEMENT_CONFIRMED, {})


async def _handle_ready(lobby_code: str, player_id: str) -> None:
    lobby = lobby_manager.get(lobby_code)
    if not lobby:
        return

    player = lobby.players.get(player_id)
    if not player:
        return

    if not player.ships_placed:
        await ws_manager.send(player_id, EVT_ERROR, {"message": "Place your ships before marking ready"})
        return

    player.ready = True

    all_ready = (
        len(lobby.players) == 2
        and all(p.ready and p.ships_placed for p in lobby.players.values())
    )

    if all_ready:
        lobby_manager.start_game(lobby_code)
        ids = lobby.player_ids()
        first = ids[0]
        await ws_manager.broadcast(ids, EVT_GAME_START, {
            "first_turn": first,
            "players": {pid: lobby.players[pid].username for pid in ids},
        })
        await ws_manager.send(first, EVT_YOUR_TURN, {})


async def _handle_fire(lobby_code: str, player_id: str, data: dict) -> None:
    try:
        msg = FireMsg.model_validate(data)
    except ValidationError:
        await ws_manager.send(player_id, EVT_ERROR, {"message": "Invalid fire data"})
        return

    lobby = lobby_manager.get(lobby_code)
    if not lobby or not lobby.engine:
        await ws_manager.send(player_id, EVT_ERROR, {"message": "Game not started"})
        return

    # DR-1: all game logic validated server-side
    result = lobby.engine.fire(player_id, msg.row, msg.col)
    if not result["valid"]:
        await ws_manager.send(player_id, EVT_ERROR, {"message": result.get("reason", "Invalid move")})
        return

    ids = lobby.player_ids()

    # DR-4: broadcast only hit/miss/sunk — never ship positions
    await ws_manager.broadcast(ids, EVT_SHOT_RESULT, {
        "row": msg.row,
        "col": msg.col,
        "hit": result["hit"],
        "sunk": result["sunk"],
        "ship_name": result.get("ship_name"),
        "shooter": player_id,
    })

    if result.get("winner"):
        await ws_manager.broadcast(ids, EVT_GAME_OVER, {
            "winner": result["winner"],
            "winner_username": lobby.players[result["winner"]].username,
        })
    elif result.get("next_turn"):
        await ws_manager.send(result["next_turn"], EVT_YOUR_TURN, {})

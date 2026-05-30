from fastapi import APIRouter, HTTPException

from ..server.lobby_manager import lobby_manager

router = APIRouter(prefix="/api/game", tags=["game"])


@router.get("/{lobby_code}/state")
def get_game_state(lobby_code: str, player_id: str):
    lobby = lobby_manager.get(lobby_code.upper())
    if not lobby:
        raise HTTPException(status_code=404, detail="Lobby not found")
    if player_id not in lobby.players:
        raise HTTPException(status_code=403, detail="Forbidden")  # DR-8: no internal detail
    if not lobby.engine:
        return {"status": lobby.status, "board": None}
    return {
        "status": lobby.status,
        "board": lobby.engine.board_view_for(player_id),  # DR-4: own view only
        "current_turn": lobby.engine.state.current_turn,
        "winner": lobby.engine.state.winner,
    }

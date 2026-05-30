from .player import Player
from .game_state import GameState, GameStatus

BOARD_SIZE = 10


class GameEngine:
    def __init__(self, player1: Player, player2: Player) -> None:
        self._players: dict[str, Player] = {
            player1.player_id: player1,
            player2.player_id: player2,
        }
        self._order: list[str] = [player1.player_id, player2.player_id]
        self.state = GameState(current_turn=player1.player_id)

    def fire(self, attacker_id: str, row: int, col: int) -> dict:
        if self.state.status != GameStatus.IN_PROGRESS:
            return {"valid": False, "reason": "Game is not in progress"}
        if self.state.current_turn != attacker_id:
            return {"valid": False, "reason": "Not your turn"}
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return {"valid": False, "reason": "Coordinates out of range"}  # DR-1

        defender_id = self._opponent(attacker_id)
        result = self._players[defender_id].board.receive_shot(row, col)
        if not result["valid"]:
            return result

        if self._players[defender_id].board.all_sunk:
            self.state.status = GameStatus.FINISHED
            self.state.winner = attacker_id
            result["next_turn"] = None
        else:
            self.state.current_turn = defender_id
            result["next_turn"] = defender_id

        result["winner"] = self.state.winner
        return result

    def board_view_for(self, viewer_id: str) -> dict:
        """Return only what the viewer is allowed to see. DR-4: no opponent ship positions."""
        opponent_id = self._opponent(viewer_id)
        viewer = self._players[viewer_id]
        opponent = self._players[opponent_id]

        return {
            "your_ships": [
                {"name": s.name, "cells": s.cells, "is_sunk": s.is_sunk}
                for s in viewer.board.ships
            ],
            "shots_received": viewer.board.shots_received(),
            "shots_fired": opponent.board.shots_received(),
        }

    def _opponent(self, player_id: str) -> str:
        return self._order[1] if player_id == self._order[0] else self._order[0]

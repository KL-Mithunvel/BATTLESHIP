from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from ..server.lobby_manager import lobby_manager
from ..server.session_manager import session_manager
from ..game.rules import validate_username

router = APIRouter(prefix="/api/lobby", tags=["lobby"])


class UsernameRequest(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def clean(cls, v: str) -> str:
        ok, result = validate_username(v)  # DR-5: sanitize on entry
        if not ok:
            raise ValueError(result)
        return result


@router.post("/create")
def create_lobby(req: UsernameRequest):
    player_id = session_manager.create(req.username)
    lobby = lobby_manager.create(player_id, req.username)
    return {"lobby_code": lobby.code, "player_id": player_id}


@router.post("/join/{lobby_code}")
def join_lobby(lobby_code: str, req: UsernameRequest):
    code = lobby_code.upper()
    player_id = session_manager.create(req.username)
    lobby, error = lobby_manager.join(code, player_id, req.username)
    if not lobby:
        session_manager.remove(player_id)
        raise HTTPException(status_code=400, detail=error)
    return {"lobby_code": lobby.code, "player_id": player_id}


@router.get("/{lobby_code}")
def get_lobby(lobby_code: str):
    lobby = lobby_manager.get(lobby_code.upper())
    if not lobby:
        raise HTTPException(status_code=404, detail="Lobby not found")
    return {
        "code": lobby.code,
        "status": lobby.status,
        "player_count": len(lobby.players),
    }

import json
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, player_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[player_id] = ws

    def disconnect(self, player_id: str) -> None:
        self._connections.pop(player_id, None)

    def is_connected(self, player_id: str) -> bool:
        return player_id in self._connections

    async def send(self, player_id: str, event: str, data: dict) -> None:
        ws = self._connections.get(player_id)
        if ws:
            try:
                await ws.send_text(json.dumps({"event": event, "data": data}))
            except Exception:
                self.disconnect(player_id)

    async def broadcast(self, player_ids: list[str], event: str, data: dict) -> None:
        for pid in player_ids:
            await self.send(pid, event, data)


ws_manager = WebSocketManager()
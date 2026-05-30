# Claude Log

## 2026-05-30 — Initial scaffold: FastAPI backend + React frontend

- Read all docs in .CLAUDE/ and README.md to understand project conventions
- Decided tech stack with user: FastAPI backend, React frontend, WebSocket for real-time turns
- Incorporated friend's architecture doc (more granular game engine, server/ folder, REST routes)
- Added 8 binding security Development Rules (DR-1 through DR-8) to CLAUDE.md after user highlighted internet safety concern; user clarified these belong in CLAUDE.md not memory
- Corrected memory placement: auto-memory is for cross-project personal preferences; project rules go in .CLAUDE/CLAUDE.md
- Built complete backend:
  - game/: ship.py, board.py, player.py, game_state.py, rules.py, engine.py
  - server/: lobby.py, lobby_manager.py, session_manager.py, websocket_manager.py, events.py
  - api/: health_routes.py, lobby_routes.py, game_routes.py
  - main.py: FastAPI app with CORS (DR-7), WS auth (DR-6), Pydantic message validation (DR-2)
- Built complete frontend:
  - hooks/: useWebSocket.js (stale-closure-safe), useGame.js (reducer-based state)
  - components/: Board.jsx + Board.css, ShipYard.jsx (click-to-place + randomize)
  - pages/: Lobby.jsx (create/join), Game.jsx (waiting → placement → in_progress → finished)
- Game not yet run/tested — tests are next milestone (see TODO.md)
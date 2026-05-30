# TODO

## In Progress

## Done
- [x] Define project tech stack: FastAPI + React + WebSocket
- [x] Define architecture with security rules DR-1 through DR-8
- [x] Scaffold full backend: game engine, lobby manager, WebSocket manager, REST API
- [x] Scaffold full frontend: Lobby, Game, Board, ShipYard, hooks
- [x] Write pytest tests: 96/96 passing (ship, board, rules, engine, lobby_manager)
- [x] setup.bat: one-time setup with venv, npm install, and test run
- [x] run.py: single command starts backend + frontend + opens browser

## Not Started
- [ ] Add reconnection support (rejoin an in-progress game after disconnect)
- [ ] Add rate limiting to WebSocket fire messages (prevent spam)
- [ ] LAN mode: display host machine's local IP on the waiting screen
- [ ] Chat messages during game (optional stretch)
- [ ] Lobby expiry / cleanup of stale lobbies
- [ ] Production deployment config (Dockerfile, env var checklist)

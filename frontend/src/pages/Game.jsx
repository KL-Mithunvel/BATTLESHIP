import { useState, useMemo } from 'react'
import { useGame } from '../hooks/useGame.js'
import { useWebSocket } from '../hooks/useWebSocket.js'
import Board from '../components/Board.jsx'
import ShipYard from '../components/ShipYard.jsx'

const SHIP_SIZES = { carrier: 5, battleship: 4, cruiser: 3, submarine: 3, destroyer: 2 }

function buildMyBoard(placements, shotsReceived) {
  const grid = Array(10).fill(null).map(() => Array(10).fill(null))
  for (const p of placements) {
    const size = SHIP_SIZES[p.name] ?? 3
    for (let i = 0; i < size; i++) {
      const r = p.horizontal ? p.row : p.row + i
      const c = p.horizontal ? p.col + i : p.col
      if (r >= 0 && r < 10 && c >= 0 && c < 10) grid[r][c] = 'ship'
    }
  }
  for (const s of shotsReceived) {
    grid[s.row][s.col] = s.hit ? 'hit' : 'miss'
  }
  return grid
}

function buildOpponentBoard(myShots) {
  const grid = Array(10).fill(null).map(() => Array(10).fill(null))
  for (const s of myShots) {
    grid[s.row][s.col] = s.hit ? 'hit' : 'miss'
  }
  return grid
}

export default function Game({ session, onLeave }) {
  const [myPlacements, setMyPlacements] = useState([])

  const { state, handleEvent } = useGame(session.playerID)
  const { send }               = useWebSocket(session.lobbyCode, session.playerID, handleEvent)

  const myBoardCells       = useMemo(() => buildMyBoard(myPlacements, state.shotsReceived), [myPlacements, state.shotsReceived])
  const opponentBoardCells = useMemo(() => buildOpponentBoard(state.myShots), [state.myShots])

  function handleSubmit(placements) {
    setMyPlacements(placements)
    send('place_ships', { placements })
  }

  function handleReady() {
    send('player_ready', {})
  }

  // ── Waiting for opponent ──
  if (state.phase === 'lobby') {
    return (
      <div className="game-waiting">
        <h2>Your Game Code</h2>
        <div className="lobby-code">{session.lobbyCode}</div>
        <p className="copy-hint">Share this code with your opponent</p>
        <p className="status-msg">Waiting for opponent to join…</p>
        {state.notification && <p className="error-msg">{state.notification}</p>}
        <button className="secondary" onClick={onLeave}>Leave</button>
      </div>
    )
  }

  // ── Ship placement ──
  if (state.phase === 'placement') {
    return (
      <div className="game-placement">
        <h2>Place Your Ships</h2>
        {state.opponentUsername && (
          <p className="status-msg">Playing against {state.opponentUsername}</p>
        )}
        <ShipYard
          onSubmit={handleSubmit}
          onReady={handleReady}
          confirmed={state.placementConfirmed}
          disabled={false}
        />
        {state.notification && <p className="error-msg" style={{ marginTop: 12 }}>{state.notification}</p>}
      </div>
    )
  }

  // ── In progress / finished ──
  const isFinished = state.phase === 'finished'
  const iWon = state.winner === session.playerID

  return (
    <div className="game-board">
      {isFinished ? (
        <div className="game-over-banner">
          {iWon ? '🏆 You win!' : 'You lose — better luck next time!'}
        </div>
      ) : (
        <div className="game-status">
          {state.isMyTurn
            ? 'Your turn — click the opponent board to fire'
            : "Opponent's turn…"}
        </div>
      )}

      {state.notification && <p className="error-msg" style={{ textAlign: 'center', marginBottom: 12 }}>{state.notification}</p>}

      <div className="boards">
        <Board
          label="Your Board"
          cells={myBoardCells}
        />
        <Board
          label={`${state.opponentUsername ?? 'Opponent'}'s Board`}
          cells={opponentBoardCells}
          interactive={state.isMyTurn && !isFinished}
          onCellClick={(r, c) => send('fire', { row: r, col: c })}
        />
      </div>

      {isFinished && (
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <button className="primary" onClick={onLeave}>Back to Menu</button>
        </div>
      )}
    </div>
  )
}

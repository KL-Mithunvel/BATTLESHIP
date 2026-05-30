import { useReducer, useCallback } from 'react'

const INITIAL = {
  phase: 'lobby',           // lobby | placement | in_progress | finished
  placementConfirmed: false,
  isMyTurn: false,
  myShots: [],              // [{row, col, hit, sunk}] — shots I fired at opponent
  shotsReceived: [],        // [{row, col, hit}]       — shots opponent fired at me
  winner: null,             // player_id of winner
  winnerUsername: null,
  opponentUsername: null,
  notification: null,
}

function reducer(state, { type, data, playerID }) {
  switch (type) {
    case 'placement_phase':
      return { ...state, phase: 'placement' }

    case 'opponent_joined':
      return { ...state, opponentUsername: data.username, notification: null }

    case 'placement_confirmed':
      return { ...state, placementConfirmed: true }

    case 'game_start':
      return {
        ...state,
        phase: 'in_progress',
        isMyTurn: data.first_turn === playerID,
      }

    case 'shot_result':
      if (data.shooter === playerID) {
        return {
          ...state,
          myShots: [...state.myShots, { row: data.row, col: data.col, hit: data.hit, sunk: data.sunk }],
          isMyTurn: false,
        }
      }
      return {
        ...state,
        shotsReceived: [...state.shotsReceived, { row: data.row, col: data.col, hit: data.hit }],
      }

    case 'your_turn':
      return { ...state, isMyTurn: true }

    case 'game_over':
      return {
        ...state,
        phase: 'finished',
        winner: data.winner,
        winnerUsername: data.winner_username,
        isMyTurn: false,
      }

    case 'opponent_disconnected':
      return { ...state, notification: 'Opponent disconnected.' }

    case 'error':
      return { ...state, notification: data.message }

    default:
      return state
  }
}

export function useGame(playerID) {
  const [state, dispatch] = useReducer(reducer, INITIAL)

  const handleEvent = useCallback((event, data) => {
    dispatch({ type: event, data, playerID })
  }, [playerID])

  return { state, handleEvent }
}

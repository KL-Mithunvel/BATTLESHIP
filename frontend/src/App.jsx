import { useState } from 'react'
import Lobby from './pages/Lobby.jsx'
import Game from './pages/Game.jsx'

export default function App() {
  const [session, setSession] = useState(null)
  // session: { playerID, lobbyCode, username }

  return session
    ? <Game session={session} onLeave={() => setSession(null)} />
    : <Lobby onJoin={setSession} />
}

import { useState } from 'react'

const SAFE_USERNAME = /[^A-Za-z0-9 ]/g

export default function Lobby({ onJoin }) {
  const [username, setUsername] = useState('')
  const [code, setCode]         = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  const sanitize = (s) => s.replace(SAFE_USERNAME, '').slice(0, 20)

  async function create() {
    if (!username.trim()) return setError('Enter a username')
    setLoading(true); setError('')
    try {
      const res  = await fetch('/api/lobby/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim() }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail ?? 'Failed to create game')
      onJoin({ playerID: data.player_id, lobbyCode: data.lobby_code, username: username.trim() })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function join() {
    if (!username.trim()) return setError('Enter a username')
    if (!code.trim())     return setError('Enter a lobby code')
    setLoading(true); setError('')
    try {
      const res  = await fetch(`/api/lobby/join/${code.trim().toUpperCase()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim() }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail ?? 'Failed to join game')
      onJoin({ playerID: data.player_id, lobbyCode: data.lobby_code, username: username.trim() })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="lobby">
      <h1>BATTLESHIP</h1>
      <p className="lobby-subtitle">Naval strategy · Play with friends over the internet</p>

      <div className="lobby-card">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          value={username}
          onChange={e => setUsername(sanitize(e.target.value))}
          placeholder="Your name (letters & numbers)"
          maxLength={20}
          autoComplete="off"
          onKeyDown={e => e.key === 'Enter' && create()}
        />

        <button className="primary" onClick={create} disabled={loading}>
          Create Game
        </button>

        <div className="lobby-divider">— or join an existing game —</div>

        <div className="lobby-row">
          <input
            value={code}
            onChange={e => setCode(e.target.value.replace(/[^A-Za-z0-9]/g, '').toUpperCase().slice(0, 6))}
            placeholder="Lobby code"
            maxLength={6}
            autoComplete="off"
            onKeyDown={e => e.key === 'Enter' && join()}
          />
          <button className="secondary" onClick={join} disabled={loading} style={{ whiteSpace: 'nowrap' }}>
            Join
          </button>
        </div>

        {error && <p className="error-msg">{error}</p>}
      </div>
    </div>
  )
}

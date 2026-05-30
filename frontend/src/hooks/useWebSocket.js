import { useEffect, useRef, useCallback } from 'react'

export function useWebSocket(lobbyCode, playerID, onMessage) {
  // Keep a ref so the WS callback always calls the latest version of onMessage
  // without needing to reconnect every render.
  const onMessageRef = useRef(onMessage)
  useEffect(() => { onMessageRef.current = onMessage })

  const wsRef = useRef(null)

  useEffect(() => {
    if (!lobbyCode || !playerID) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${lobbyCode}/${playerID}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      try {
        const { event, data } = JSON.parse(e.data)
        onMessageRef.current(event, data)
      } catch {
        // ignore unparseable server messages
      }
    }

    ws.onerror = () => {
      onMessageRef.current('error', { message: 'Connection error — try refreshing.' })
    }

    return () => ws.close()
  }, [lobbyCode, playerID]) // only reconnect when these change

  const send = useCallback((event, data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ event, data }))
    }
  }, [])

  return { send }
}

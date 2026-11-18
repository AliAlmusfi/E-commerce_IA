import { useEffect, useRef, useState } from 'react'

export function useWebSocket(path, token, onMessage) {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    if (!path || !token) return

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = import.meta.env.VITE_WS_URL || `${window.location.hostname}:8000`
    const url = `${protocol}://${host}${path}?token=${token}`

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setIsConnected(true)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (err) {
        console.error('[WebSocket] Parse error:', err)
      }
    }

    ws.onerror = (error) => console.error('[WebSocket] Error:', error)
    ws.onclose = () => setIsConnected(false)

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close()
    }
  }, [path, token, onMessage])

  return { isConnected }
}
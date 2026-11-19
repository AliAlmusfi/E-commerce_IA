import { useEffect, useRef, useState } from 'react'

export function useWebSocket(path, token, onMessage) {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  
  const onMessageRef = useRef(onMessage)
  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  useEffect(() => {
    if (!path || !token) return

    let isCancelled = false

    const connect = () => {
      if (isCancelled) return

      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const host = import.meta.env.VITE_WS_URL || `${window.location.hostname}:8000`
      const url = `${protocol}://${host}${path}?token=${token}`

      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        if (isCancelled) return
        console.log(`[WebSocket] Connected to ${path}`)
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (onMessageRef.current) onMessageRef.current(data)
        } catch (err) {
          console.error('[WebSocket] Parse error:', err)
        }
      }

    //   ws.onerror = () => {
        
    //   }

      ws.onclose = () => {
        if (isCancelled) return
        setIsConnected(false)
        
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log(`[WebSocket] Reconnecting to ${path}...`)
          connect()
        }, 3000)
      }
    }

    connect()

    return () => {
      isCancelled = true
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [path, token]) 

  return { isConnected }
}
import { useEffect, useRef, useState } from 'react'

const NON_RETRYABLE_CODES = new Set([1000, 4001, 4003])

export function useWebSocket(
  path,
  token,
  onMessage,
  { maxRetries = 50, reconnectDelay = 3000, stabilityMs = 5000 } = {}
) {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const stableTimeoutRef = useRef(null)
  const retriesRef = useRef(0)
  const isCancelledRef = useRef(false)

  const onMessageRef = useRef(onMessage)
  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  useEffect(() => {
    if (!path || !token) return

    isCancelledRef.current = false
    retriesRef.current = 0

    const normalizedPath = path.startsWith('/') ? path : `/${path}`
    let host = import.meta.env.VITE_WS_URL || `${window.location.hostname}:8000`
    host = host.replace(/^(wss?|https?):\/\//, '')

    const connect = () => {
      if (isCancelledRef.current) return

      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const url = `${protocol}://${host}${normalizedPath}?token=${encodeURIComponent(token)}`

      let ws
      try {
        ws = new WebSocket(url)
      } catch {
        return
      }
      wsRef.current = ws

      ws.onopen = () => {
        if (isCancelledRef.current) {
          ws.close(1000, 'Cancelled')
          return
        }
        console.log(`[WS] ✅ Connected to ${normalizedPath}`)
        setIsConnected(true)

        stableTimeoutRef.current = setTimeout(() => {
          if (ws.readyState === WebSocket.OPEN) {
            retriesRef.current = 0
          }
        }, stabilityMs)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (onMessageRef.current) onMessageRef.current(data)
        } catch (err) {
          console.error('[WS] Parse error:', err)
        }
      }

      ws.onclose = (event) => {
        if (stableTimeoutRef.current) {
          clearTimeout(stableTimeoutRef.current)
          stableTimeoutRef.current = null
        }

        if (isCancelledRef.current) return
        setIsConnected(false)
        console.warn(`[WS] Closed ${normalizedPath} | code=${event.code} reason=${event.reason || '—'}`)

        if (NON_RETRYABLE_CODES.has(event.code)) return

        if (retriesRef.current >= maxRetries) {
          console.error(`[WS] ❌ Giving up after ${maxRetries} retries for ${normalizedPath}`)
          return
        }

        retriesRef.current += 1
        console.log(`[WS] 🔄 Reconnecting (${retriesRef.current}/${maxRetries})...`)
        reconnectTimeoutRef.current = setTimeout(connect, reconnectDelay)
      }
    }

    connect()

    return () => {
      isCancelledRef.current = true
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      if (stableTimeoutRef.current) clearTimeout(stableTimeoutRef.current)

      const ws = wsRef.current
      wsRef.current = null
      if (!ws) return

      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000, 'Component unmounted')
      } else if (ws.readyState === WebSocket.CONNECTING) {
        ws.onopen = () => ws.close(1000, 'Component unmounted')
      }
    }
  }, [path, token, maxRetries, reconnectDelay, stabilityMs])

  return { isConnected }
}

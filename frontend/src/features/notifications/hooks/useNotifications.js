import { useEffect, useState } from 'react'

export function useNotifications(wsUrl) {
  const [messages, setMessages] = useState([])

  useEffect(() => {
    if (!wsUrl) return
    const ws = new WebSocket(wsUrl)
    ws.onmessage = (ev) => setMessages(prev => [...prev, JSON.parse(ev.data)])
    return () => ws.close()
  }, [wsUrl])

  return { messages }
}
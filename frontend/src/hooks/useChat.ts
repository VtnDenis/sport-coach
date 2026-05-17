import { useState, useRef, useCallback } from 'react'
import { chatSSE } from '../api/client'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const sendMessage = useCallback(async (sessionId: string, text: string) => {
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
    }
    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    const assistantId = crypto.randomUUID()
    const assistantMsg: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      isStreaming: true,
    }
    setMessages((prev) => [...prev, assistantMsg])

    abortRef.current = chatSSE(
      sessionId,
      text,
      (chunk) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + chunk } : m
          )
        )
      },
      (full) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: full, isStreaming: false }
              : m
          )
        )
        setIsLoading(false)
      },
      (err) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: `Error: ${err}`, isStreaming: false }
              : m
          )
        )
        setIsLoading(false)
      }
    )
  }, [])

  const clearChat = useCallback(() => {
    abortRef.current?.abort()
    setMessages([])
    setIsLoading(false)
  }, [])

  return { messages, isLoading, sendMessage, clearChat }
}

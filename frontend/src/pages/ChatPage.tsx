import { useCallback, useEffect, useRef } from 'react'
import { useChat } from '../hooks/useChat'
import { createSession } from '../api/client'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'

export default function ChatPage() {
  const { messages, isLoading, sendMessage, clearChat } = useChat()
  const sessionIdRef = useRef<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    createSession().then((id) => {
      sessionIdRef.current = id
    })
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleNewChat = useCallback(() => {
    clearChat()
    createSession().then((id) => {
      sessionIdRef.current = id
    })
  }, [clearChat])

  const handleSend = useCallback(
    (text: string) => {
      if (!sessionIdRef.current) return
      sendMessage(sessionIdRef.current, text)
    },
    [sendMessage]
  )

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b bg-white flex justify-between items-center">
        <h2 className="font-semibold text-gray-800">Chat</h2>
        <button
          onClick={handleNewChat}
          className="text-xs text-blue-600 hover:text-blue-800"
        >
          New Chat
        </button>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-lg font-medium">Welcome to Sport Coach</p>
            <p className="text-sm mt-2">
              Ask me about your runs, health stats, or get personalized running advice.
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
      </div>

      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  )
}

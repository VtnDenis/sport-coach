import { ChatMessage as ChatMessageType } from '../hooks/useChat'

interface Props {
  message: ChatMessageType
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
           style={{ backgroundColor: isUser ? '#3b82f6' : '#22c55e', color: 'white' }}>
        {isUser ? 'U' : 'C'}
      </div>
      <div className={`max-w-[75%] rounded-lg px-4 py-2 ${isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'}`}>
        <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        {message.isStreaming && (
          <span className="inline-block w-1.5 h-4 bg-gray-600 animate-pulse ml-0.5 align-text-bottom" />
        )}
      </div>
    </div>
  )
}

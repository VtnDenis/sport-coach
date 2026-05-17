import { useState, useCallback } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import DashboardPage from './pages/DashboardPage'

export default function App() {
  const [chatKey, setChatKey] = useState(0)

  const handleNewChat = useCallback(() => {
    setChatKey((k) => k + 1)
  }, [])

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        <Sidebar onNewChat={handleNewChat} />
        <main className="flex-1 flex flex-col overflow-hidden">
          <Routes>
            <Route path="/" element={<ChatPage key={chatKey} />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

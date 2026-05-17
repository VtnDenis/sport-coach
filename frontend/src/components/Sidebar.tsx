import { NavLink } from 'react-router-dom'

interface Props {
  onNewChat: () => void
}

export default function Sidebar({ onNewChat }: Props) {
  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-full">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-bold">Sport Coach</h1>
        <p className="text-xs text-gray-400 mt-0.5">Your running companion</p>
      </div>

      <button
        onClick={onNewChat}
        className="mx-3 mt-4 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
      >
        + New Chat
      </button>

      <nav className="mt-6 flex flex-col gap-1 px-3">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `px-3 py-2 rounded-lg text-sm transition-colors ${isActive ? 'bg-gray-700 text-white' : 'text-gray-400 hover:bg-gray-800'}`
          }
        >
          Chat
        </NavLink>
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `px-3 py-2 rounded-lg text-sm transition-colors ${isActive ? 'bg-gray-700 text-white' : 'text-gray-400 hover:bg-gray-800'}`
          }
        >
          Dashboard
        </NavLink>
      </nav>
    </aside>
  )
}

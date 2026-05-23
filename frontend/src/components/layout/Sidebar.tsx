import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Home,
  BarChart3,
  AlertCircle,
  History,
  Settings,
  ChevronLeft,
} from 'lucide-react'

const Sidebar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(true)
  const location = useLocation()

  const menuItems = [
    { label: 'Home', icon: Home, path: '/' },
    { label: 'Dashboard', icon: BarChart3, path: '/dashboard' },
    { label: 'Alerts', icon: AlertCircle, path: '/alerts' },
    { label: 'History', icon: History, path: '/history' },
    { label: 'Settings', icon: Settings, path: '/settings' },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <aside
      className={`${
        isOpen ? 'w-64' : 'w-20'
      } bg-gray-900 text-white transition-all duration-300 flex flex-col fixed left-0 top-0 h-screen`}
    >
      {/* Logo */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        {isOpen && <h2 className="text-lg font-bold">Weather</h2>}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 hover:bg-gray-800 rounded transition-colors"
        >
          <ChevronLeft className={`w-5 h-5 transition-transform ${isOpen ? '' : 'rotate-180'}`} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-sky-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {isOpen && <span className="text-sm font-medium">{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className={`flex items-center space-x-3 ${isOpen ? '' : 'justify-center'}`}>
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex-shrink-0" />
          {isOpen && (
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">User</p>
              <p className="text-xs text-gray-400 truncate">Active</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}

export default Sidebar

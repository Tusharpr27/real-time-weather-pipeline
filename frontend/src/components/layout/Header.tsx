import React from 'react'
import { Menu, Bell, Settings as SettingsIcon, LogOut } from 'lucide-react'
import useNotifications from '@/hooks/useNotifications'
import NotificationsDropdown from '@/components/notifications/NotificationsDropdown'
import { useAppSelector } from '@/store/hooks'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

interface HeaderProps {
  onMenuClick?: () => void
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const activeCount = useAppSelector((state) => state.alerts.activeCount)
  const user = useAppSelector((state) => state.user.user)
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [showDropdown, setShowDropdown] = React.useState(false)

  // Start polling notifications (default 15s)
  useNotifications()

  // close dropdown when clicking outside
  React.useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest?.('.header-notifications')) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('click', onDocClick)
    return () => document.removeEventListener('click', onDocClick)
  }, [])

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Menu className="w-6 h-6 text-gray-600" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900">Weather Pipeline</h1>
        </div>

        <div className="flex items-center space-x-6">
          {/* Notifications */}
          <div className="relative header-notifications">
            <button
              onClick={() => setShowDropdown((s) => !s)}
              className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Notifications"
            >
              <Bell className="w-6 h-6" />
              {activeCount > 0 && (
                <span className="absolute top-1 right-1 flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full">
                  {activeCount}
                </span>
              )}
            </button>

            {showDropdown && (
              <div className="absolute right-0 mt-2 z-50">
                <NotificationsDropdown />
              </div>
            )}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-3 pl-6 border-l border-gray-200">
            <button
              title="Settings"
              onClick={() => navigate('/settings')}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <SettingsIcon className="w-5 h-5" />
            </button>
            <button
              title="Logout"
              onClick={() => { console.log('Showcase mode: Logout disabled') }}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
            </button>
            <div className="flex items-center space-x-3">
              <div
                role="button"
                onClick={() => navigate('/settings')}
                className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center text-white font-semibold cursor-pointer"
              >
                {user?.full_name ? user.full_name[0].toUpperCase() : 'U'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

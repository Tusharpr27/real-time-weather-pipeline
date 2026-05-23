import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  BarChart3,
  AlertCircle,
  History,
  Settings,
  Menu,
  X,
  LogOut,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

const MobileMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { label: 'Home', icon: Home, path: '/' },
    { label: 'Dashboard', icon: BarChart3, path: '/dashboard' },
    { label: 'Alerts', icon: AlertCircle, path: '/alerts' },
    { label: 'History', icon: History, path: '/history' },
    { label: 'Settings', icon: Settings, path: '/settings' },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleClose = () => setIsOpen(false);

  return (
    <>
      {/* Mobile Menu Trigger */}
      <div className="md:hidden fixed top-0 left-0 right-0 bg-gray-900 text-white p-4 flex items-center justify-between z-40 border-b border-gray-800">
        <h1 className="text-lg font-bold">Weather Pipeline</h1>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          aria-label="Toggle menu"
        >
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-30 top-16"
          onClick={handleClose}
          aria-label="Close menu"
        />
      )}

      {/* Mobile Menu Content */}
      <div
        className={`fixed top-16 left-0 right-0 bottom-0 bg-gray-900 text-white z-30 transform transition-transform duration-300 overflow-y-auto ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:hidden`}
      >
        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={handleClose}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? 'bg-sky-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Divider */}
        <div className="border-t border-gray-800 my-4" />

        {/* User Info */}
        <div className="px-4 py-3">
          <p className="text-xs text-gray-400 mb-2">Signed in as</p>
          <p className="text-sm font-medium truncate">{user?.fullName || 'User'}</p>
          <p className="text-xs text-gray-400 truncate">{user?.email}</p>
        </div>

        {/* Logout Button */}
        <div className="px-4 py-3 space-y-2">
          <button
            onClick={() => {
              logout();
              handleClose();
            }}
            className="w-full flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span className="text-sm font-medium">Sign Out</span>
          </button>
        </div>
      </div>
    </>
  );
};

export default MobileMenu;

import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import '@styles/global.css'

// Layout Components
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'

// Pages
import Dashboard from '@/pages/Dashboard'
import Alerts from '@/pages/Alerts'
import History from '@/pages/History'
import Settings from '@/pages/Settings'

function MainLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar />
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout><Navigate to="/dashboard" replace /></MainLayout>} />
        <Route path="/dashboard" element={<MainLayout><Dashboard /></MainLayout>} />
        <Route path="/alerts" element={<MainLayout><Alerts /></MainLayout>} />
        <Route path="/history" element={<MainLayout><History /></MainLayout>} />
        <Route path="/settings" element={<MainLayout><Settings /></MainLayout>} />

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App

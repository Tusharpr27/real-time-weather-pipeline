import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import MobileMenu from './MobileMenu';
import Footer from './Footer';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
}

/**
 * ResponsiveLayout Component
 * Provides responsive layout with:
 * - Desktop sidebar (hidden on mobile)
 * - Mobile menu (visible only on mobile)
 * - Responsive header
 * - Main content area with proper spacing
 * - Responsive footer
 */
const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Desktop Sidebar - Hidden on mobile (md and below) */}
      <div className="hidden lg:flex lg:w-64 fixed h-screen left-0 top-0">
        <Sidebar />
      </div>

      {/* Mobile Menu - Only visible on mobile */}
      <div className="lg:hidden">
        <MobileMenu />
      </div>

      {/* Main Content */}
      <div className="flex flex-col flex-1 w-full lg:ml-64 pt-16 lg:pt-0">
        {/* Header */}
        <Header />

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
};

export default ResponsiveLayout;

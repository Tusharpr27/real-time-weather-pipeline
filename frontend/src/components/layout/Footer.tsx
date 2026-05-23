import React from 'react'

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <p>
            &copy; {currentYear} Real-Time Weather Data Pipeline. All rights reserved.
          </p>
          <div className="flex items-center space-x-6">
            <a href="#" className="hover:text-gray-900 transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-gray-900 transition-colors">
              Terms of Service
            </a>
            <a href="#" className="hover:text-gray-900 transition-colors">
              Documentation
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer

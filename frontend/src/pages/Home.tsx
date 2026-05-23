import React from 'react'

const Home: React.FC = () => {
  return (
    <div className="flex-1 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Weather Pipeline Dashboard
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Real-time weather monitoring and alerting system
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card bg-gradient-to-br from-blue-50 to-cyan-50">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Real-Time Data</h2>
            <p className="text-gray-600">Live weather data from multiple locations</p>
          </div>
          
          <div className="card bg-gradient-to-br from-amber-50 to-orange-50">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Smart Alerts</h2>
            <p className="text-gray-600">Automated alerts with intelligent escalation</p>
          </div>
          
          <div className="card bg-gradient-to-br from-emerald-50 to-teal-50">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Analytics</h2>
            <p className="text-gray-600">Comprehensive weather trends and statistics</p>
          </div>
        </div>

        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Getting Started</h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-md bg-blue-500 text-white text-sm font-medium">
                1
              </span>
              <p className="ml-3 text-gray-600">Navigate to Dashboard to view real-time weather data</p>
            </div>
            <div className="flex items-start">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-md bg-blue-500 text-white text-sm font-medium">
                2
              </span>
              <p className="ml-3 text-gray-600">Check Alerts for active advisories and escalations</p>
            </div>
            <div className="flex items-start">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-md bg-blue-500 text-white text-sm font-medium">
                3
              </span>
              <p className="ml-3 text-gray-600">Review History to analyze trends and patterns</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home

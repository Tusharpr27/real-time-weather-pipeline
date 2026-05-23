import React from 'react'
import { useAlerts } from '@/hooks/useAlerts'
import { useNavigate } from 'react-router-dom'

export const NotificationsDropdown: React.FC = () => {
  const { items, loading, acknowledge, resolve, getAlerts } = useAlerts()
  const navigate = useNavigate()

  const recent = items.slice(0, 5)

  return (
    <div className="w-80 bg-white shadow-lg rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-sm">Notifications</h4>
        <button
          onClick={() => getAlerts({ page: 1, pageSize: 10 })}
          className="text-xs text-gray-500 hover:underline"
        >
          Refresh
        </button>
      </div>

      {loading && <div className="text-sm text-gray-500">Loading...</div>}

      {!loading && recent.length === 0 && (
        <div className="text-sm text-gray-500">No active alerts</div>
      )}

      <ul className="space-y-2">
        {recent.map((a) => (
          <li key={a.id} className="border-b pb-2">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-sm font-medium">{a.title || a.alert_type || 'Alert'}</div>
                <div className="text-xs text-gray-500">{a.location}</div>
              </div>
              <div className="ml-2 text-right text-xs">
                <div className={`px-2 py-1 rounded ${a.severity === 'HIGH' ? 'bg-red-100 text-red-700' : a.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}`}>
                  {a.severity}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between mt-2">
              <div className="text-xs text-gray-600 truncate">{a.message}</div>
              <div className="flex items-center space-x-2 ml-2">
                <button
                  onClick={() => acknowledge(a.id)}
                  className="text-xs text-blue-600 hover:underline"
                >
                  Ack
                </button>
                <button
                  onClick={() => resolve(a.id)}
                  className="text-xs text-gray-600 hover:underline"
                >
                  Resolve
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>

      <div className="mt-3 text-center">
        <button
          onClick={() => navigate('/alerts')}
          className="text-sm text-indigo-600 hover:underline"
        >
          View all alerts
        </button>
      </div>
    </div>
  )
}

export default NotificationsDropdown

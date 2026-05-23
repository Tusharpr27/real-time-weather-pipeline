import { useEffect, useCallback } from 'react'
import { useAlerts } from './useAlerts'

export const useNotifications = (pollIntervalMs = 15000) => {
  const { activeCount, items, getAlerts } = useAlerts()

  // Initial fetch + polling
  useEffect(() => {
    getAlerts({ page: 1, pageSize: 10 })
    const id = setInterval(() => {
      getAlerts({ page: 1, pageSize: 10 })
    }, pollIntervalMs)

    return () => clearInterval(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollIntervalMs])

  const refresh = useCallback(() => {
    getAlerts({ page: 1, pageSize: 10 })
  }, [getAlerts])

  return {
    activeCount,
    items,
    refresh,
  }
}

export default useNotifications

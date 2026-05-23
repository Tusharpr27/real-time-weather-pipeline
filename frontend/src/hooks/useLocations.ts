import { useState, useEffect } from 'react'
import api from '@/services/api'

export const useLocations = () => {
  const [locations, setLocations] = useState<Array<{ id: string; name: string }>>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    api
      .getLocations()
      .then((data: any[]) => {
        if (!mounted) return
        // Map backend locations: use `name` as id to match weather endpoints
        const mapped = (data || []).map((l) => ({ id: String(l.name), name: l.name }))
        setLocations(mapped)
      })
      .catch((err) => {
        if (!mounted) return
        setError(err?.message || 'Failed to load locations')
      })
      .finally(() => {
        if (!mounted) return
        setLoading(false)
      })

    return () => {
      mounted = false
    }
  }, [])

  return { locations, loading, error }
}

export default useLocations

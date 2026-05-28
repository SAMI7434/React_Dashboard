import { useEffect, useState } from 'react'
import { getDashboard } from '../api/ingest.js'

export const useDashboard = () => {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = () => {
    setIsLoading(true)
    setError(null)
    getDashboard()
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load dashboard'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [])

  return { data, isLoading, error, refresh }
}

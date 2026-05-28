import { useEffect, useState } from 'react'
import { getIssues } from '../api/ingest.js'

export const useIssues = () => {
  const [issues, setIssues] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = () => {
    setIsLoading(true)
    setError(null)
    getIssues()
      .then((data) => setIssues(data))
      .catch((err) => setError(err.message || 'Failed to load issues'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [])

  return { issues, isLoading, error, refresh }
}

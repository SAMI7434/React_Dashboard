import { useEffect, useState } from 'react'
import { getUploads } from '../api/ingest.js'

export const useUploads = () => {
  const [uploads, setUploads] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = () => {
    setIsLoading(true)
    setError(null)
    getUploads()
      .then((data) => setUploads(data))
      .catch((err) => setError(err.message || 'Failed to load uploads'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [])

  return { uploads, isLoading, error, refresh }
}

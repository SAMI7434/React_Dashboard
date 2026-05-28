import { useEffect, useMemo, useState } from 'react'
import { getRecords } from '../api/ingest.js'

export const useRecords = (filters = {}) => {
  const [records, setRecords] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const query = useMemo(() => {
    const params = {}
    if (filters.status) {
      params.status = filters.status
    }
    if (filters.meterId) {
      params.meter_id = filters.meterId
    }
    if (filters.originalUnit) {
      params.original_energy_unit = filters.originalUnit
    }
    return params
  }, [filters.meterId, filters.originalUnit, filters.status])

  const refresh = () => {
    setIsLoading(true)
    setError(null)
    getRecords(query)
      .then((data) => setRecords(data))
      .catch((err) => setError(err.message || 'Failed to load records'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [query])

  return { records, isLoading, error, refresh }
}

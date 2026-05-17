import { useState, useEffect } from 'react'
import { getDashboardSummary } from '../api/client'

export interface DashboardData {
  recent_activities: Array<{
    id: number
    name: string
    type: string
    start_date: string
    distance_m: number
    moving_time_s: number
    average_heartrate: number
  }>
  health: Record<string, unknown> | null
  sleep: Record<string, unknown> | null
  training_status: Record<string, unknown> | null
}

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = () => {
    setLoading(true)
    getDashboardSummary()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [])

  return { data, loading, refresh }
}

import { useDashboard } from '../hooks/useDashboard'
import StatsCard from '../components/StatsCard'
import PaceChart from '../components/PaceChart'

function formatPace(movingTimeS: number | undefined, distanceM: number | undefined): string {
  if (!movingTimeS || !distanceM || distanceM === 0) return '-'
  const paceMinPerKm = movingTimeS / 60 / (distanceM / 1000)
  const min = Math.floor(paceMinPerKm)
  const sec = Math.round((paceMinPerKm - min) * 60)
  return `${min}:${sec.toString().padStart(2, '0')}`
}

function formatTime(s: number): string {
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  if (h > 0) return `${h}h ${m}m`
  return `${m}m ${sec}s`
}

export default function DashboardPage() {
  const { data, loading, refresh } = useDashboard()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400">Loading dashboard...</p>
      </div>
    )
  }

  const activities = data?.recent_activities || []
  const health = data?.health
  const sleep = data?.sleep
  const training = data?.training_status

  const totalDistance = activities.reduce((sum, a) => sum + (a.distance_m || 0), 0) / 1000
  const totalTime = activities.reduce((sum, a) => sum + (a.moving_time_s || 0), 0)

  const chartData = activities.map((a) => ({
    label: new Date(a.start_date).toLocaleDateString('en-US', { weekday: 'short' }),
    value: (a.distance_m || 0) / 1000,
  }))

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-800">Dashboard</h2>
        <button
          onClick={refresh}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Total Distance" value={totalDistance.toFixed(1)} unit="km" color="#3b82f6" />
        <StatsCard title="Total Time" value={formatTime(totalTime)} color="#22c55e" />
        <StatsCard title="Activities" value={activities.length} color="#f59e0b" />
        <StatsCard
          title="Avg Pace"
          value={activities.length > 0 ? formatPace(totalTime, totalDistance * 1000) : '-'}
          unit="/km"
          color="#ef4444"
        />
      </div>

      {health && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Resting HR"
            value={health?.resting_heart_rate as number ?? '-'}
            unit="bpm"
            color="#8b5cf6"
          />
          <StatsCard
            title="Stress Level"
            value={health?.average_stress as number ?? '-'}
            color="#ec4899"
          />
          <StatsCard
            title="Body Battery"
            value={health?.body_battery?.highest as number ?? '-'}
            color="#14b8a6"
          />
          {sleep?.sleep_score && (
            <StatsCard
              title="Sleep Score"
              value={sleep.sleep_score as number}
              color="#6366f1"
            />
          )}
        </div>
      )}

      <PaceChart
        title="Distance (km) - Last Activities"
        data={chartData}
        color="#3b82f6"
        unit="km"
      />

      {training?.vo2max && (
        <div className="bg-white rounded-xl p-4 shadow-sm border">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Training Status</h3>
          <div className="flex gap-6">
            <div>
              <p className="text-xs text-gray-400">VO2max</p>
              <p className="text-lg font-bold text-gray-800">{training.vo2max}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Status</p>
              <p className="text-lg font-bold text-gray-800">{training.training_status ?? '-'}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

interface Props {
  title: string
  value: string | number
  unit?: string
  color?: string
}

export default function StatsCard({ title, value, unit, color = '#3b82f6' }: Props) {
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold mt-1" style={{ color }}>
        {value}
        {unit && <span className="text-sm font-normal text-gray-400 ml-1">{unit}</span>}
      </p>
    </div>
  )
}

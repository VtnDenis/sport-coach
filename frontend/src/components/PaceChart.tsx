import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

interface DataPoint {
  label: string
  value: number
}

interface Props {
  title: string
  data: DataPoint[]
  color?: string
  unit?: string
}

export default function PaceChart({ title, data, color = '#3b82f6', unit }: Props) {
  const chartData = {
    labels: data.map((d) => d.label),
    datasets: [
      {
        label: title,
        data: data.map((d) => d.value),
        borderColor: color,
        backgroundColor: color + '20',
        fill: true,
        tension: 0.3,
        pointRadius: 4,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      y: {
        title: { display: !!unit, text: unit || '' },
        grid: { color: '#f0f0f0' },
      },
      x: {
        grid: { display: false },
      },
    },
  }

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border">
      <h3 className="text-sm font-medium text-gray-600 mb-3">{title}</h3>
      <div className="h-48">
        <Line data={chartData} options={options} />
      </div>
    </div>
  )
}

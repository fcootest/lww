import { useEffect, useState } from 'react'
import api from '../services/api'

interface DashboardData {
  summary: {
    pending: number
    in_progress: number
    completed: number
    overdue: number
  }
  by_type: {
    copyright: number
    trademark: number
    policy: number
    contract: number
  }
}

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .get('/api/legal/dashboard')
      .then((res) => { const d = res.data?.data || res.data; setData(d?.summary ? d : null); })
      .catch((err) => setError(err.message || 'Failed to load dashboard'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div data-testid="dashboard-page">
        <div data-testid="loading-state" className="text-gray-500">Loading dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div data-testid="dashboard-page">
        <div data-testid="error-state" className="text-red-500">Error: {error}</div>
      </div>
    )
  }

  return (
    <div data-testid="dashboard-page">
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div data-testid="card-pending" className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-400">
          <h3 className="text-sm font-medium text-gray-500">Pending</h3>
          <p className="text-2xl font-bold">{data?.summary?.pending ?? 0}</p>
        </div>
        <div data-testid="card-in-progress" className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-400">
          <h3 className="text-sm font-medium text-gray-500">In Progress</h3>
          <p className="text-2xl font-bold">{data?.summary?.in_progress ?? 0}</p>
        </div>
        <div data-testid="card-completed" className="bg-white rounded-lg shadow p-4 border-l-4 border-green-400">
          <h3 className="text-sm font-medium text-gray-500">Completed</h3>
          <p className="text-2xl font-bold">{data?.summary?.completed ?? 0}</p>
        </div>
        <div data-testid="card-overdue" className="bg-white rounded-lg shadow p-4 border-l-4 border-red-400">
          <h3 className="text-sm font-medium text-gray-500">Overdue</h3>
          <p className="text-2xl font-bold">{data?.summary?.overdue ?? 0}</p>
        </div>
      </div>

      {/* By Type Section */}
      <div data-testid="by-type-section">
        <h3 className="text-lg font-semibold mb-4">By Type</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="text-sm font-medium text-gray-500">Copyright</h4>
            <p className="text-xl font-bold">{data?.by_type?.copyright ?? 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="text-sm font-medium text-gray-500">Trademark</h4>
            <p className="text-xl font-bold">{data?.by_type?.trademark ?? 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="text-sm font-medium text-gray-500">Policy</h4>
            <p className="text-xl font-bold">{data?.by_type?.policy ?? 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="text-sm font-medium text-gray-500">Contract</h4>
            <p className="text-xl font-bold">{data?.by_type?.contract ?? 0}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

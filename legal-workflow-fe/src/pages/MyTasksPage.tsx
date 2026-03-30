import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

interface Task {
  id: number
  code: string
  title: string
  type_l1: string
  status: string
  due_date: string
}

interface TasksResponse {
  items: Task[]
  total: number
  page: number
  page_size: number
}

const STATUS_COLORS: Record<string, string> = {
  COMPLETED: 'bg-green-100 text-green-800',
  APPROVED: 'bg-emerald-100 text-emerald-800',
  SUBMITTED: 'bg-amber-100 text-amber-800',
  IN_PROGRESS: 'bg-blue-100 text-blue-800',
  PENDING: 'bg-gray-100 text-gray-800',
  REJECTED: 'bg-red-100 text-red-800',
}

export function MyTasksPage() {
  const navigate = useNavigate()
  const [data, setData] = useState<TasksResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [filterType, setFilterType] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  useEffect(() => {
    setLoading(true)
    const params: Record<string, string | number> = { page, page_size: pageSize }
    if (filterType) params.type_l1 = filterType
    if (filterStatus) params.status = filterStatus

    api
      .get('/api/legal/my-tasks', { params })
      .then((res) => setData(res.data?.data || res.data))
      .catch(() => setData({ items: [], total: 0, page: 1, page_size: pageSize }))
      .finally(() => setLoading(false))
  }, [page, pageSize, filterType, filterStatus])

  const totalPages = data ? Math.ceil(data.total / pageSize) : 0

  return (
    <div data-testid="my-tasks-page">
      <h2 className="text-2xl font-bold mb-6">My Tasks</h2>

      {/* Filter Bar */}
      <div data-testid="filter-bar" className="flex gap-4 mb-4">
        <select
          data-testid="filter-type"
          className="border rounded px-3 py-2"
          value={filterType}
          onChange={(e) => { setFilterType(e.target.value); setPage(1) }}
        >
          <option value="">All Types</option>
          <option value="COPYRIGHT">Copyright</option>
          <option value="TRADEMARK">Trademark</option>
          <option value="POLICY">Policy</option>
          <option value="CONTRACT">Contract</option>
        </select>

        <select
          data-testid="filter-status"
          className="border rounded px-3 py-2"
          value={filterStatus}
          onChange={(e) => { setFilterStatus(e.target.value); setPage(1) }}
        >
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="COMPLETED">Completed</option>
          <option value="APPROVED">Approved</option>
          <option value="SUBMITTED">Submitted</option>
          <option value="REJECTED">Rejected</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <div data-testid="loading-state" className="text-gray-500">Loading tasks...</div>
      ) : (
        <>
          <table data-testid="tasks-table" className="w-full bg-white rounded-lg shadow">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left p-3">Code</th>
                <th className="text-left p-3">Title</th>
                <th className="text-left p-3">Submitted By</th>
                <th className="text-left p-3">Type</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Due Date</th>
                <th className="text-left p-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {data && data?.items?.length > 0 ? (
                data?.items?.map((task) => (
                  <tr
                    key={task.tsi_id}
                    className="border-b hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/legal/tasks/${task.tsi_id}`)}
                  >
                    <td className="p-3 font-mono text-sm">{task.tsi_code}</td>
                    <td className="p-3">{task.title}</td>
                    <td className="p-3 text-sm">{task.submitted_by_name || '-'}</td>
                    <td className="p-3">{task.tst_l1_name}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[task.status] || 'bg-gray-100'}`}>
                        {task.status}
                      </span>
                    </td>
                    <td className="p-3">{task.due_date}</td>
                    <td className="p-3">
                      <button
                        className="text-blue-600 hover:underline text-sm"
                        onClick={(e) => { e.stopPropagation(); navigate(`/legal/tasks/${task.tsi_id}`) }}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-gray-500" data-testid="no-tasks">
                    No tasks found
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div data-testid="pagination" className="flex justify-center gap-2 mt-4">
              <button
                className="px-3 py-1 border rounded disabled:opacity-50"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </button>
              <span className="px-3 py-1">
                Page {page} of {totalPages}
              </span>
              <button
                className="px-3 py-1 border rounded disabled:opacity-50"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

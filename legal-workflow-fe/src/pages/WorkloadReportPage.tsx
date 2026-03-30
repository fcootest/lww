import { useEffect, useState } from 'react'

interface WorkloadRow {
  emp_id: string
  emp_code: string
  emp_name: string
  task_count: number
  completed_count: number
  pending_count: number
}

export function WorkloadReportPage() {
  const [data, setData] = useState<WorkloadRow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/legal/reports/workload', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
    })
      .then((r) => r.json())
      .then((res) => {
        if (res.success) setData(res.data)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h1>Workload Report</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Employee</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Code</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Total Tasks</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Completed</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Pending</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.emp_id}>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.emp_name}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.emp_code}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.task_count}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.completed_count}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.pending_count}</td>
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: 16 }}>
                  No data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  )
}

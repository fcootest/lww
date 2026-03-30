import { useEffect, useState } from 'react'

interface SLARow {
  tst_id: string
  tst_code: string
  tst_name: string
  sla_days: number
  on_time: number
  late: number
  total: number
  sla_compliance_rate: number
}

export function SLAReportPage() {
  const [data, setData] = useState<SLARow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/legal/reports/sla', {
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
      <h1>SLA Compliance Report</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Task Type</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>SLA (days)</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>On Time</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Late</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Total</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>Compliance %</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.tst_id}>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.tst_name}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.sla_days}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.on_time}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.late}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.total}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{row.sla_compliance_rate}%</td>
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: 16 }}>
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

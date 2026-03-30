import { useEffect, useState } from 'react'
import api from '../services/api'

interface FilterConfig {
  id: number
  tst_l1: string
  field_name: string
  field_type: string
  required: boolean
  options?: string[]
}

export function ConfigFiltersPage() {
  const [filters, setFilters] = useState<FilterConfig[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/api/legal/config/filters')
      .then((res) => setFilters(res.data))
      .catch(() => setFilters([]))
      .finally(() => setLoading(false))
  }, [])

  // Group filters by TST L1
  const grouped = filters.reduce<Record<string, FilterConfig[]>>((acc, f) => {
    if (!acc[f.tst_l1]) acc[f.tst_l1] = []
    acc[f.tst_l1].push(f)
    return acc
  }, {})

  return (
    <div data-testid="config-filters-page">
      <h2 className="text-2xl font-bold mb-6">Filter Configuration</h2>

      {loading ? (
        <div className="text-gray-500">Loading filters...</div>
      ) : (
        <div className="space-y-6">
          {Object.keys(grouped).length > 0 ? (
            Object.entries(grouped).map(([tstL1, fields]) => (
              <div key={tstL1} className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-3">{tstL1}</h3>
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2 text-sm">Field Name</th>
                      <th className="text-left p-2 text-sm">Type</th>
                      <th className="text-left p-2 text-sm">Required</th>
                      <th className="text-left p-2 text-sm">Options</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fields.map((f) => (
                      <tr key={f.id} className="border-b">
                        <td className="p-2 text-sm">{f.field_name}</td>
                        <td className="p-2 text-sm">{f.field_type}</td>
                        <td className="p-2 text-sm">
                          <span className={f.required ? 'text-red-600' : 'text-gray-400'}>
                            {f.required ? 'Yes' : 'No'}
                          </span>
                        </td>
                        <td className="p-2 text-sm">
                          {f.options ? f.options.join(', ') : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))
          ) : (
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-500">No filter configurations found</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

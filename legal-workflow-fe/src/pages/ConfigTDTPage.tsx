import { useEffect, useState } from 'react'
import api from '../services/api'

interface DocType {
  id: number
  code: string
  name: string
  description: string
  allowed_extensions: string[]
}

export function ConfigTDTPage() {
  const [docTypes, setDocTypes] = useState<DocType[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/api/legal/config/tdt')
      .then((res) => setDocTypes(res.data))
      .catch(() => setDocTypes([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div data-testid="config-tdt-page">
      <h2 className="text-2xl font-bold mb-6">Task Document Types (TDT)</h2>

      {loading ? (
        <div className="text-gray-500">Loading document types...</div>
      ) : (
        <div className="bg-white rounded-lg shadow">
          {docTypes.length > 0 ? (
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left p-3 text-sm">Code</th>
                  <th className="text-left p-3 text-sm">Name</th>
                  <th className="text-left p-3 text-sm">Description</th>
                  <th className="text-left p-3 text-sm">Allowed Extensions</th>
                </tr>
              </thead>
              <tbody>
                {docTypes.map((dt) => (
                  <tr key={dt.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 font-mono text-sm">{dt.code}</td>
                    <td className="p-3 text-sm">{dt.name}</td>
                    <td className="p-3 text-sm text-gray-600">{dt.description}</td>
                    <td className="p-3 text-sm">
                      <div className="flex flex-wrap gap-1">
                        {dt.allowed_extensions.map((ext) => (
                          <span key={ext} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                            {ext}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="p-6 text-gray-500">No document types configured</p>
          )}
        </div>
      )}
    </div>
  )
}

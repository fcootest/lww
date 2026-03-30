import { useEffect, useState } from 'react'
import api from '../services/api'

interface Role {
  id: number
  code: string
  name: string
  description: string
  permissions: string[]
}

export function ConfigTRTPage() {
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/api/legal/config/trt')
      .then((res) => setRoles(res.data))
      .catch(() => setRoles([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div data-testid="config-trt-page">
      <h2 className="text-2xl font-bold mb-6">Task Role Tree (TRT)</h2>

      {loading ? (
        <div className="text-gray-500">Loading roles...</div>
      ) : (
        <div className="bg-white rounded-lg shadow">
          {roles.length > 0 ? (
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left p-3 text-sm">Code</th>
                  <th className="text-left p-3 text-sm">Name</th>
                  <th className="text-left p-3 text-sm">Description</th>
                  <th className="text-left p-3 text-sm">Permissions</th>
                </tr>
              </thead>
              <tbody>
                {roles.map((role) => (
                  <tr key={role.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 font-mono text-sm">{role.code}</td>
                    <td className="p-3 text-sm">{role.name}</td>
                    <td className="p-3 text-sm text-gray-600">{role.description}</td>
                    <td className="p-3 text-sm">
                      <div className="flex flex-wrap gap-1">
                        {role.permissions.map((perm) => (
                          <span key={perm} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
                            {perm}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="p-6 text-gray-500">No roles configured</p>
          )}
        </div>
      )}
    </div>
  )
}

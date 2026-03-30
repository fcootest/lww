import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../../stores/auth.store'

const commonMenuItems = [
  { path: '/legal', label: 'Dashboard', icon: '📊' },
  { path: '/legal/tasks', label: 'My Tasks', icon: '📋' },
  { path: '/legal/tasks/new', label: 'Create Task', icon: '➕' },
]

const adminMenuItems = [
  { path: '/legal/config/tst', label: 'Config TST', icon: '🔧' },
  { path: '/legal/config/filters', label: 'Filters', icon: '🔍' },
  { path: '/legal/reports/sla', label: 'SLA Report', icon: '⏱️' },
  { path: '/legal/reports/workload', label: 'Workload', icon: '📈' },
  { path: '/legal/settings', label: 'Settings', icon: '⚙️' },
]

const SEC_BADGE_COLORS: Record<string, string> = {
  SEC1: 'bg-blue-500',
  SEC2: 'bg-yellow-500',
  SEC3: 'bg-purple-500',
  SEC4: 'bg-emerald-500',
}

export function Sidebar() {
  const { user, clearAuth } = useAuthStore()
  const empsec = user?.empsec || 'SEC1'
  const isAdmin = empsec === 'SEC4' || user?.role === 'ADMIN'
  const displayName = user?.emp_name || 'User'

  return (
    <aside className="w-56 bg-gray-900 text-white h-screen sticky top-0 flex flex-col" data-testid="sidebar">
      <div className="px-4 py-3 border-b border-gray-800">
        <h1 className="text-lg font-bold">Legal Workflow</h1>
      </div>

      <nav className="flex-1 px-2 py-2 overflow-y-auto">
        <ul className="space-y-0.5">
          {[...commonMenuItems, ...(isAdmin ? adminMenuItems : [])].map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
                  }`
                }
                data-testid={`menu-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <span className="text-sm">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="px-3 py-3 border-t border-gray-800">
        {user && (
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${SEC_BADGE_COLORS[empsec] || 'bg-gray-500'}`} data-testid="sec-badge">
              {empsec}
            </span>
            <div className="min-w-0">
              <p className="text-sm text-gray-200 truncate">{displayName}</p>
              <p className="text-xs text-gray-500">{user.role_legal || 'User'}</p>
            </div>
          </div>
        )}
        <button
          onClick={() => { clearAuth(); window.location.href = '/login' }}
          className="w-full text-left px-2 py-1.5 rounded text-xs text-gray-400 hover:bg-gray-800 transition-colors"
          data-testid="btn-switch-user"
        >
          Switch User / Logout
        </button>
      </div>
    </aside>
  )
}

const menuItems = [...commonMenuItems, ...adminMenuItems]
export { menuItems }

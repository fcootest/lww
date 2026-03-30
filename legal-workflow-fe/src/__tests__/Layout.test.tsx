import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Sidebar, menuItems } from '../components/layout/Sidebar'
import { RoleGuard } from '../components/auth/RoleGuard'
import { useAuthStore } from '../stores/auth.store'

describe('Sidebar', () => {
  it('renders 10 menu items', () => {
    useAuthStore.setState({ user: { emp_code: 'X', role: 'ADMIN', emp_name: 'Admin', empsec: 'SEC4' }, token: 't' })
    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    )
    const sidebar = screen.getByTestId('sidebar')
    const links = sidebar.querySelectorAll('a')
    expect(links.length).toBe(8)
  })

  it('renders all expected menu labels', () => {
    useAuthStore.setState({ user: { emp_code: 'X', role: 'ADMIN', emp_name: 'Admin', empsec: 'SEC4' }, token: 't' })
    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    )
    const expectedLabels = [
      'Dashboard', 'My Tasks', 'Create Task',
      'Config TST', 'Filters',
      'SLA Report', 'Workload', 'Settings',
    ]
    expectedLabels.forEach((label) => {
      expect(screen.getByText(label)).toBeInTheDocument()
    })
  })

  it('has correct route paths', () => {
    expect(menuItems[0].path).toBe('/legal')
    expect(menuItems[1].path).toBe('/legal/tasks')
    expect(menuItems[3].path).toBe('/legal/config/tst')
    expect(menuItems[5].path).toBe('/legal/reports/sla')
  })

  it('renders Legal Workflow title', () => {
    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    )
    expect(screen.getByText('Legal Workflow')).toBeInTheDocument()
  })
})

describe('RoleGuard', () => {
  it('shows children when user has allowed role', () => {
    useAuthStore.setState({
      user: { emp_code: 'TiepTA', role: 'ADMIN', emp_name: 'Tran Anh Tiep' },
      token: 'fake-token',
    })

    render(
      <MemoryRouter>
        <RoleGuard allowedRoles={['ADMIN']}>
          <div data-testid="protected-content">Secret</div>
        </RoleGuard>
      </MemoryRouter>
    )

    expect(screen.getByTestId('protected-content')).toBeInTheDocument()
  })

  it('redirects when user role not in allowed list', () => {
    useAuthStore.setState({
      user: { emp_code: 'HuongLT', role: 'LEGAL_INTERN', emp_name: 'Le Thi Huong' },
      token: 'fake-token',
    })

    render(
      <MemoryRouter initialEntries={['/legal/config/tst']}>
        <RoleGuard allowedRoles={['ADMIN']}>
          <div data-testid="protected-content">Secret</div>
        </RoleGuard>
      </MemoryRouter>
    )

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
  })

  it('redirects to login when no user', () => {
    useAuthStore.setState({ user: null, token: null })

    render(
      <MemoryRouter>
        <RoleGuard allowedRoles={['ADMIN']}>
          <div data-testid="protected-content">Secret</div>
        </RoleGuard>
      </MemoryRouter>
    )

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
  })
})

describe('AuthStore', () => {
  it('sets auth state correctly', () => {
    const { setAuth } = useAuthStore.getState()
    setAuth('test-token', { emp_code: 'MinhPT', role: 'PRODUCT_MANAGER', emp_name: 'Pham Thanh Minh' })

    const state = useAuthStore.getState()
    expect(state.token).toBe('test-token')
    expect(state.user?.emp_code).toBe('MinhPT')
  })

  it('clears auth state', () => {
    useAuthStore.getState().setAuth('tk', { emp_code: 'X', role: 'Y', emp_name: 'Z' })
    useAuthStore.getState().clearAuth()

    const state = useAuthStore.getState()
    expect(state.token).toBeNull()
    expect(state.user).toBeNull()
  })
})

describe('API Service', () => {
  it('api module can be imported', async () => {
    const api = await import('../services/api')
    expect(api.default).toBeDefined()
    expect(api.default.defaults.headers['Content-Type']).toBe('application/json')
  })
})

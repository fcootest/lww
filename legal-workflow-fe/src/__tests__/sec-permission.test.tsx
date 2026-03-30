import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { useAuthStore } from '../stores/auth.store'
import { SecGuard } from '../components/auth/SecGuard'

// Step 9: Permission Store tests
describe('Auth Store SEC Fields', () => {
  beforeEach(() => {
    useAuthStore.getState().clearAuth()
  })

  it('stores SEC permission fields', () => {
    useAuthStore.getState().setAuth('token123', {
      emp_code: 'F.00011',
      emp_name: 'TrangPH',
      role: 'PRODUCT_MANAGER',
      empsec: 'SEC1',
      pt_allowed: 'MyPT',
      cdt_allowed: 'MyCDT',
      krf_level: 3,
      cdt_1: 'HQ1',
      role_legal: 'User',
      google_email: 'trangph@apero.vn',
    })

    const state = useAuthStore.getState()
    expect(state.user?.empsec).toBe('SEC1')
    expect(state.user?.pt_allowed).toBe('MyPT')
    expect(state.user?.krf_level).toBe(3)
  })

  it('clearAuth removes SEC fields', () => {
    useAuthStore.getState().setAuth('tok', {
      emp_code: 'X', emp_name: 'X', role: 'X', empsec: 'SEC4',
    })
    useAuthStore.getState().clearAuth()
    expect(useAuthStore.getState().user).toBeNull()
  })

  it('initial state has no SEC fields', () => {
    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
  })

  it('User interface includes SEC fields', () => {
    useAuthStore.getState().setAuth('t', {
      emp_code: 'F.00041', emp_name: 'HoangDNH', role: 'ADMIN',
      empsec: 'SEC4', pt_allowed: 'AllPT', cdt_allowed: 'AllCDT',
      krf_level: 7, google_email: 'hoangdnh@apero.vn',
    })
    const u = useAuthStore.getState().user!
    expect(u.empsec).toBe('SEC4')
    expect(u.pt_allowed).toBe('AllPT')
    expect(u.cdt_allowed).toBe('AllCDT')
    expect(u.krf_level).toBe(7)
  })
})

// Step 11: SecGuard tests
describe('SecGuard Component', () => {
  beforeEach(() => {
    useAuthStore.getState().clearAuth()
  })

  it('allows matching SEC level', () => {
    useAuthStore.getState().setAuth('t', {
      emp_code: 'X', emp_name: 'X', role: 'X', empsec: 'SEC4',
    })
    render(<SecGuard minLevel="SEC4"><div data-testid="content">Visible</div></SecGuard>)
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('blocks insufficient SEC level', () => {
    useAuthStore.getState().setAuth('t', {
      emp_code: 'X', emp_name: 'X', role: 'X', empsec: 'SEC1',
    })
    render(<SecGuard minLevel="SEC4"><div data-testid="content">Hidden</div></SecGuard>)
    expect(screen.queryByTestId('content')).toBeNull()
  })

  it('allows higher SEC level for lower requirement', () => {
    useAuthStore.getState().setAuth('t', {
      emp_code: 'X', emp_name: 'X', role: 'X', empsec: 'SEC3',
    })
    render(<SecGuard minLevel="SEC2"><div data-testid="content">OK</div></SecGuard>)
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('handles roleLegal check', () => {
    useAuthStore.getState().setAuth('t', {
      emp_code: 'X', emp_name: 'X', role: 'X', empsec: 'SEC4', role_legal: 'Approver',
    })
    render(<SecGuard roleLegal="Approver"><div data-testid="content">OK</div></SecGuard>)
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('blocks wrong roleLegal', () => {
    useAuthStore.getState().setAuth('t', {
      emp_code: 'X', emp_name: 'X', role: 'X', empsec: 'SEC1', role_legal: 'User',
    })
    render(<SecGuard roleLegal="Approver"><div data-testid="content">Hidden</div></SecGuard>)
    expect(screen.queryByTestId('content')).toBeNull()
  })
})

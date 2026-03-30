import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from '../pages/DashboardPage'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: { request: { use: vi.fn() } },
    defaults: { headers: { 'Content-Type': 'application/json' } },
  },
}))

import api from '../services/api'

const mockDashboardData = {
  summary: { pending: 5, in_progress: 3, completed: 10, overdue: 2 },
  by_type: { copyright: 4, trademark: 3, policy: 8, contract: 5 },
}

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders 4 summary cards', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockDashboardData })

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByTestId('card-pending')).toBeInTheDocument()
    })

    expect(screen.getByTestId('card-in-progress')).toBeInTheDocument()
    expect(screen.getByTestId('card-completed')).toBeInTheDocument()
    expect(screen.getByTestId('card-overdue')).toBeInTheDocument()
  })

  it('renders type breakdown section', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockDashboardData })

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByTestId('by-type-section')).toBeInTheDocument()
    })

    expect(screen.getByText('By Type')).toBeInTheDocument()
    expect(screen.getByText('Copyright')).toBeInTheDocument()
    expect(screen.getByText('Trademark')).toBeInTheDocument()
    expect(screen.getByText('Policy')).toBeInTheDocument()
    expect(screen.getByText('Contract')).toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    vi.mocked(api.get).mockReturnValueOnce(new Promise(() => {}))

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    expect(screen.getByTestId('loading-state')).toBeInTheDocument()
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument()
  })

  it('shows dashboard title', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockDashboardData })

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
    })
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { MyTasksPage } from '../pages/MyTasksPage'

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

const mockTasksData = {
  items: [
    { id: 1, code: 'LGL-001', title: 'Copyright Review', type_l1: 'COPYRIGHT', status: 'PENDING', due_date: '2026-04-01' },
    { id: 2, code: 'LGL-002', title: 'Trademark Filing', type_l1: 'TRADEMARK', status: 'IN_PROGRESS', due_date: '2026-04-15' },
  ],
  total: 2,
  page: 1,
  page_size: 10,
}

describe('MyTasksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders table with column headers', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTasksData })

    render(
      <MemoryRouter>
        <MyTasksPage />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByTestId('tasks-table')).toBeInTheDocument()
    })

    expect(screen.getByText('Code')).toBeInTheDocument()
    expect(screen.getByText('Title')).toBeInTheDocument()
    expect(screen.getByText('Type')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
    expect(screen.getByText('Due Date')).toBeInTheDocument()
    expect(screen.getByText('Action')).toBeInTheDocument()
  })

  it('filter controls render', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTasksData })

    render(
      <MemoryRouter>
        <MyTasksPage />
      </MemoryRouter>
    )

    expect(screen.getByTestId('filter-bar')).toBeInTheDocument()
    expect(screen.getByTestId('filter-type')).toBeInTheDocument()
    expect(screen.getByTestId('filter-status')).toBeInTheDocument()
  })

  it('shows "No tasks" when empty', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({
      data: { items: [], total: 0, page: 1, page_size: 10 },
    })

    render(
      <MemoryRouter>
        <MyTasksPage />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByTestId('no-tasks')).toBeInTheDocument()
    })

    expect(screen.getByText('No tasks found')).toBeInTheDocument()
  })

  it('page title renders', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTasksData })

    render(
      <MemoryRouter>
        <MyTasksPage />
      </MemoryRouter>
    )

    expect(screen.getByText('My Tasks')).toBeInTheDocument()
  })
})

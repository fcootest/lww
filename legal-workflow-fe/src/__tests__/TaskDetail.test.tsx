import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { TaskDetailPage } from '../pages/TaskDetailPage'

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

const mockTaskDetail = {
  id: 1,
  code: 'LGL-001',
  title: 'Copyright Review Request',
  status: 'IN_PROGRESS',
  requester: 'John Doe',
  assignee: 'Jane Smith',
  created_at: '2026-03-01',
  due_date: '2026-04-01',
  type_l1: 'COPYRIGHT',
  progress_tree: [
    {
      id: 1,
      code: 'TST-1',
      name: 'Initial Review',
      status: 'COMPLETED',
      children: [
        { id: 2, code: 'TST-1.1', name: 'Document Check', status: 'COMPLETED', children: [] },
        { id: 3, code: 'TST-1.2', name: 'Legal Analysis', status: 'IN_PROGRESS', children: [] },
      ],
    },
  ],
  documents: [
    { id: 1, file_name: 'contract.pdf', version: 1, uploaded_by: 'John Doe', uploaded_at: '2026-03-01' },
    { id: 2, file_name: 'amendment.docx', version: 2, uploaded_by: 'Jane Smith', uploaded_at: '2026-03-10' },
  ],
  event_log: [
    { id: 1, action: 'Task Created', actor: 'John Doe', created_at: '2026-03-01', detail: 'Initial creation' },
    { id: 2, action: 'Status Changed', actor: 'Jane Smith', created_at: '2026-03-05', detail: 'Moved to IN_PROGRESS' },
  ],
}

function renderWithRouter() {
  return render(
    <MemoryRouter initialEntries={['/legal/tasks/1']}>
      <Routes>
        <Route path="/legal/tasks/:id" element={<TaskDetailPage />} />
      </Routes>
    </MemoryRouter>
  )
}

describe('TaskDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders task info header', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTaskDetail })

    renderWithRouter()

    await waitFor(() => {
      expect(screen.getByTestId('task-info-header')).toBeInTheDocument()
    })

    expect(screen.getByText('Copyright Review Request')).toBeInTheDocument()
    expect(screen.getAllByText('IN_PROGRESS').length).toBeGreaterThanOrEqual(1)
  })

  it('renders progress tree section', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTaskDetail })

    renderWithRouter()

    await waitFor(() => {
      expect(screen.getByTestId('progress-tree-section')).toBeInTheDocument()
    })

    expect(screen.getByText('Progress Tree')).toBeInTheDocument()
  })

  it('renders documents section', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTaskDetail })

    renderWithRouter()

    await waitFor(() => {
      expect(screen.getByTestId('documents-section')).toBeInTheDocument()
    })

    expect(screen.getByText('Documents')).toBeInTheDocument()
    expect(screen.getByText('contract.pdf')).toBeInTheDocument()
    expect(screen.getByText('amendment.docx')).toBeInTheDocument()
  })

  it('renders event log section', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTaskDetail })

    renderWithRouter()

    await waitFor(() => {
      expect(screen.getByTestId('event-log-section')).toBeInTheDocument()
    })

    expect(screen.getByText('Event Log')).toBeInTheDocument()
    expect(screen.getByText('Task Created')).toBeInTheDocument()
    expect(screen.getByText('Status Changed')).toBeInTheDocument()
  })
})

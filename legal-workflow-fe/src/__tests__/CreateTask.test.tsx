import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { CreateTaskPage } from '../pages/CreateTaskPage'

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

describe('CreateTaskPage', () => {
  it('renders form with TST L1 select', () => {
    render(
      <MemoryRouter>
        <CreateTaskPage />
      </MemoryRouter>
    )

    const select = screen.getByTestId('select-tst-l1')
    expect(select).toBeInTheDocument()
    expect(select.tagName).toBe('SELECT')

    // Verify options exist
    expect(screen.getByText('COPYRIGHT')).toBeInTheDocument()
    expect(screen.getByText('TRADEMARK')).toBeInTheDocument()
    expect(screen.getByText('POLICY')).toBeInTheDocument()
    expect(screen.getByText('CONTRACT')).toBeInTheDocument()
  })

  it('title input exists', () => {
    render(
      <MemoryRouter>
        <CreateTaskPage />
      </MemoryRouter>
    )

    const input = screen.getByTestId('input-title')
    expect(input).toBeInTheDocument()
    expect(input.tagName).toBe('INPUT')
    expect(input).toHaveAttribute('type', 'text')
  })

  it('submit button exists', () => {
    render(
      <MemoryRouter>
        <CreateTaskPage />
      </MemoryRouter>
    )

    const button = screen.getByTestId('submit-button')
    expect(button).toBeInTheDocument()
    expect(button).toHaveTextContent('Create Task')
  })

  it('priority select with options', () => {
    render(
      <MemoryRouter>
        <CreateTaskPage />
      </MemoryRouter>
    )

    const select = screen.getByTestId('select-priority')
    expect(select).toBeInTheDocument()
    expect(select.tagName).toBe('SELECT')

    expect(screen.getByText('LOW')).toBeInTheDocument()
    expect(screen.getByText('MEDIUM')).toBeInTheDocument()
    expect(screen.getByText('HIGH')).toBeInTheDocument()
    expect(screen.getByText('CRITICAL')).toBeInTheDocument()
  })
})

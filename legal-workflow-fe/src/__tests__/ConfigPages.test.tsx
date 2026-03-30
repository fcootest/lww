import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ConfigTSTPage } from '../pages/ConfigTSTPage'
import { ConfigTRTPage } from '../pages/ConfigTRTPage'
import { ConfigTDTPage } from '../pages/ConfigTDTPage'
import { ConfigFiltersPage } from '../pages/ConfigFiltersPage'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn().mockReturnValue(new Promise(() => {})),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: { request: { use: vi.fn() } },
    defaults: { headers: { 'Content-Type': 'application/json' } },
  },
}))

describe('ConfigPages', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('ConfigTST renders tree title', () => {
    render(
      <MemoryRouter>
        <ConfigTSTPage />
      </MemoryRouter>
    )

    expect(screen.getByTestId('config-tst-page')).toBeInTheDocument()
    expect(screen.getByText('Task Structure Tree (TST)')).toBeInTheDocument()
  })

  it('ConfigTRT renders roles title', () => {
    render(
      <MemoryRouter>
        <ConfigTRTPage />
      </MemoryRouter>
    )

    expect(screen.getByTestId('config-trt-page')).toBeInTheDocument()
    expect(screen.getByText('Task Role Tree (TRT)')).toBeInTheDocument()
  })

  it('ConfigTDT renders doc types title', () => {
    render(
      <MemoryRouter>
        <ConfigTDTPage />
      </MemoryRouter>
    )

    expect(screen.getByTestId('config-tdt-page')).toBeInTheDocument()
    expect(screen.getByText('Task Document Types (TDT)')).toBeInTheDocument()
  })

  it('ConfigFilters renders filters title', () => {
    render(
      <MemoryRouter>
        <ConfigFiltersPage />
      </MemoryRouter>
    )

    expect(screen.getByTestId('config-filters-page')).toBeInTheDocument()
    expect(screen.getByText('Filter Configuration')).toBeInTheDocument()
  })
})

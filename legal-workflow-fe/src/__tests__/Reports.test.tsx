import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SLAReportPage } from '../pages/SLAReportPage'
import { WorkloadReportPage } from '../pages/WorkloadReportPage'

// Mock fetch
beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve({ success: true, data: [] }),
    })
  ))
})

describe('SLAReportPage', () => {
  it('renders title', () => {
    render(<SLAReportPage />)
    expect(screen.getByText('SLA Compliance Report')).toBeInTheDocument()
  })
})

describe('WorkloadReportPage', () => {
  it('renders title', () => {
    render(<WorkloadReportPage />)
    expect(screen.getByText('Workload Report')).toBeInTheDocument()
  })
})

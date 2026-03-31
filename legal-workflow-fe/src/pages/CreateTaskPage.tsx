import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const TST_L1_OPTIONS = [
  { value: 'TST-001', label: 'Copyright Check (LF210)' },
  { value: 'TST-010', label: 'Trademark Check (LF220)' },
  { value: 'TST-021', label: 'Policy Review (LF230)' },
  { value: 'TST-034', label: 'Contract Review (LF240)' },
]

const PRIORITY_OPTIONS = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']

const FILTER_FIELDS: Record<string, { filter_type: string; label: string; placeholder: string; required?: boolean }[]> = {
  'TST-001': [
    { filter_type: 'PT', label: 'Product Code *', placeholder: 'vd: APB648', required: true },
    { filter_type: 'PT_NAME', label: 'Product Name *', placeholder: 'vd: Caller ID Spam Call', required: true },
    { filter_type: 'CDT', label: 'Department (CDT)', placeholder: 'vd: HQ1, AST' },
  ],
  'TST-010': [
    { filter_type: 'PT', label: 'Product Code', placeholder: 'vd: APB648' },
    { filter_type: 'LE', label: 'Legal Entity', placeholder: 'vd: APERO-SG' },
    { filter_type: 'CTY', label: 'Country', placeholder: 'vd: US, VN' },
    { filter_type: 'TUT', label: 'Urgency', placeholder: 'NORMAL / URGENT' },
  ],
  'TST-021': [
    { filter_type: 'PT', label: 'Product Code', placeholder: 'vd: APB648' },
    { filter_type: 'LE', label: 'Legal Entity', placeholder: 'vd: APERO-SG' },
    { filter_type: 'TUT', label: 'Urgency', placeholder: 'NORMAL / URGENT' },
  ],
  'TST-034': [
    { filter_type: 'PT', label: 'Product Code', placeholder: 'vd: APB648' },
    { filter_type: 'LE', label: 'Legal Entity', placeholder: 'vd: APERO-VN' },
    { filter_type: 'CTY', label: 'Country', placeholder: 'vd: VN, SG' },
    { filter_type: 'CDT', label: 'Department', placeholder: 'vd: SAP, HQ1' },
    { filter_type: 'TLT', label: 'Transaction Type', placeholder: 'DOMESTIC / CROSS_BORDER' },
    { filter_type: 'TUT', label: 'Urgency', placeholder: 'NORMAL / URGENT' },
  ],
}

export function CreateTaskPage() {
  const navigate = useNavigate()
  const [tstId, setTstId] = useState('')
  const [title, setTitle] = useState('')
  const [priority, setPriority] = useState('MEDIUM')
  const [dueDate, setDueDate] = useState('')
  const [filterValues, setFilterValues] = useState<Record<string, string>>({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    setSuccess(null)
    try {
      // Validate required filters
      const currentFilters = FILTER_FIELDS[tstId] || []
      for (const f of currentFilters) {
        if (f.required && !filterValues[f.filter_type]?.trim()) {
          setError(`${f.label.replace(' *', '')} là bắt buộc`)
          setSubmitting(false)
          return
        }
      }
      const filters = Object.entries(filterValues)
        .filter(([, v]) => v.trim() !== '')
        .map(([filter_type, filter_code]) => ({ filter_type, filter_code: filter_code.trim() }))
      const payload = { tst_id: tstId, title, priority, due_date: dueDate || undefined, filters }
      const res = await api.post('/api/legal/task/', payload)
      const tsiId = res.data?.data?.tsi_id
      // Upload file if selected
      if (tsiId && uploadFile) {
        try {
          const formData = new FormData()
          formData.append('file', uploadFile)
          formData.append('tdt_id', 'TDT-001')
          await api.post(`/api/legal/task/${tsiId}/upload-file`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })
        } catch { /* file upload is optional, don't block task creation */ }
      }
      setSuccess('Task created: ' + tsiId)
      if (tsiId) setTimeout(() => navigate('/legal/tasks/' + tsiId), 1500)
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { detail?: string }; status?: number } }
        setError('Error: ' + JSON.stringify(axErr.response?.data?.detail || axErr.response?.status))
      } else {
        setError(err instanceof Error ? err.message : 'Failed')
      }
    } finally { setSubmitting(false) }
  }

  const filterFields = tstId ? FILTER_FIELDS[tstId] || [] : []

  return (
    <div data-testid="create-task-page">
      <h2 className="text-2xl font-bold mb-6">Create Task</h2>
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 max-w-2xl">
        {error && <div data-testid="error-message" className="mb-4 p-3 bg-red-50 text-red-700 rounded text-sm">{error}</div>}
        {success && <div className="mb-4 p-3 bg-green-50 text-green-700 rounded text-sm">{success}</div>}

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Task Type</label>
          <select data-testid="select-tst-l1" className="w-full border rounded px-3 py-2" value={tstId}
            onChange={(e) => { setTstId(e.target.value); setFilterValues({}) }} required>
            <option value="">Select Type...</option>
            {TST_L1_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input data-testid="input-title" type="text" className="w-full border rounded px-3 py-2"
            value={title} onChange={(e) => setTitle(e.target.value)}
            placeholder="vd: CopyrightReview - Caller ID App" required />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
          <select data-testid="select-priority" className="w-full border rounded px-3 py-2"
            value={priority} onChange={(e) => setPriority(e.target.value)}>
            {PRIORITY_OPTIONS.map((o) => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
          <input type="date" className="w-full border rounded px-3 py-2"
            value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
        </div>

        {filterFields.length > 0 && (
          <div data-testid="dynamic-fields" className="mb-4 border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-600 mb-3">Filters</h3>
            {filterFields.map((f) => (
              <div key={f.filter_type} className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {f.label} <span className="text-gray-400">({f.filter_type})</span>
                </label>
                <input type="text" className={`w-full border rounded px-3 py-2 ${f.required ? 'border-blue-300' : ''}`}
                  value={filterValues[f.filter_type] || ''}
                  onChange={(e) => setFilterValues(prev => ({...prev, [f.filter_type]: e.target.value}))}
                  placeholder={f.placeholder}
                  required={f.required} />
              </div>
            ))}
          </div>
        )}

        {tstId && (
          <div className="mb-4 border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-600 mb-3">Upload tài liệu</h3>
            <input ref={fileRef} type="file" accept=".pdf,.docx,.xlsx,.pptx,.png,.jpg,.csv" className="text-sm"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)} />
            {uploadFile && <p className="text-xs text-green-600 mt-1">✓ {uploadFile.name}</p>}
          </div>
        )}

        <button data-testid="submit-button" type="submit" disabled={submitting}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 font-medium">
          {submitting ? 'Creating...' : 'Create Task'}
        </button>
      </form>
    </div>
  )
}

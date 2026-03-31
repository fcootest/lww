import { useEffect, useState, useCallback, useRef } from 'react'
import { useAuthStore } from '../stores/auth.store'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'

/* Interfaces */

interface AIReviewResult {
  verdict: string
  score: number
  summary: string
  checklist: { item: string; status: string; note: string }[]
  docs_reviewed: string[]
  model: string
}

interface ProgressNode {
  tsi_id: string
  tst_id: string
  tst_name: string
  tst_level: number
  status: string
  comment?: string
  ai_review?: AIReviewResult | null
  children?: ProgressNode[]
}

interface Document {
  id?: string
  tdi_id?: string
  tsi_id?: string
  file_name: string
  file_url?: string
  version?: number
  uploaded_by?: string
  uploaded_at?: string
}

interface EventLog {
  id?: string
  created_at?: string
  event_type?: string
  emp_id?: string
  event_data?: string
}

interface Filter {
  filter_type?: string
  filter_code?: string
}

interface TaskInstance {
  tsi_id?: string
  tsi_code?: string
  title?: string
  status?: string
  priority?: string
  due_date?: string
  assigned_to?: string
  created_at?: string
}

interface TaskDetail {
  tsi: TaskInstance
  progress: ProgressNode[]
  documents: Document[]
  events: EventLog[]
  assignments: unknown[]
  filters: Filter[]
}

/* Constants */

const STATUS_COLORS: Record<string, string> = {
  COMPLETED: 'bg-green-100 text-green-800',
  APPROVED: 'bg-emerald-100 text-emerald-800',
  SUBMITTED: 'bg-amber-100 text-amber-800',
  IN_PROGRESS: 'bg-blue-100 text-blue-800',
  PENDING: 'bg-gray-100 text-gray-800',
  REJECTED: 'bg-red-100 text-red-800',
}

const EVENT_COLORS: Record<string, string> = {
  APPROVE: 'bg-green-100 text-green-800',
  REJECT: 'bg-red-100 text-red-800',
  COMMENT: 'bg-blue-100 text-blue-800',
  UPLOAD: 'bg-purple-100 text-purple-800',
  CREATE: 'bg-gray-100 text-gray-800',
  UPDATE: 'bg-yellow-100 text-yellow-800',
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8100'

function resolveFileUrl(url: string | undefined): string {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/api/')) return API_BASE + url
  return url
}

const ACCEPTED_FILE_TYPES = '.pdf,.docx,.xlsx,.pptx,.png,.jpg,.csv'

/* Helpers */

function statusIcon(status: string): string {
  switch (status) {
    case 'COMPLETED':
    case 'APPROVED':
      return '✅'
    case 'SUBMITTED':
      return '📤'
    case 'IN_PROGRESS':
      return '🔵'
    case 'REJECTED':
      return '❌'
    default:
      return '⚪'
  }
}

function findActiveL3(nodes: ProgressNode[]): ProgressNode | null {
  for (const l1 of nodes) {
    for (const l2 of l1.children || []) {
      for (const l3 of l2.children || []) {
        if (l3.status === 'IN_PROGRESS' || l3.status === 'PENDING' || l3.status === 'REJECTED') {
          return l3
        }
      }
    }
  }
  return null
}

/* Component */

export function TaskDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const authUser = useAuthStore((s) => s.user)
  const isAdmin = authUser?.role === 'ADMIN'

  const [task, setTask] = useState<TaskDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reviewState, setReviewState] = useState<Record<string, { action: string; comment: string }>>({})
  const [savingId, setSavingId] = useState<string | null>(null)
  const [showEventLog, setShowEventLog] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [uploadFileName, setUploadFileName] = useState('')
  const [uploadFileUrl, setUploadFileUrl] = useState('')
  const [actionMsg, setActionMsg] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [aiReviewingId, setAiReviewingId] = useState<string | null>(null)
  const [expandedAiReview, setExpandedAiReview] = useState<Record<string, boolean>>({})
  const [aiCheckResult, setAiCheckResult] = useState<AIReviewResult | null>(null)
  const [aiChecking, setAiChecking] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [lf240Meta, setLf240Meta] = useState<Record<string, string>>({})
  const [savingMeta, setSavingMeta] = useState(false)
  const [assignableEmps, setAssignableEmps] = useState<{emp_code: string; emp_name: string}[]>([])
  const [reassigning, setReassigning] = useState(false)

  const fetchTask = useCallback(async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const res = await api.get(`/api/legal/task/${id}`)
      let data = res.data?.data || res.data
      if (data?.tsi?.my_parent_task) {
        let rootId = data.tsi.my_parent_task
        let safety = 10
        while (rootId && safety-- > 0) {
          const parentRes = await api.get(`/api/legal/task/${rootId}`)
          const parentData = parentRes.data?.data || parentRes.data
          if (parentData?.tsi?.my_parent_task) {
            rootId = parentData.tsi.my_parent_task
          } else {
            data = parentData
            break
          }
        }
      }
      setTask(data)
      // Load metadata for LF240
      try {
        const metaRes = await api.get(`/api/legal/task/${data.tsi?.tsi_id || id}/metadata`)
        const metaData = metaRes.data?.data
        if (metaData && typeof metaData === 'object') {
          setLf240Meta(metaData)
        }
      } catch { /* metadata might not exist yet */ }
      // Load assignable employees for reassignment
      try {
        const empRes = await api.get('/api/legal/emp/')
        const empData = empRes.data?.data || empRes.data
        if (Array.isArray(empData)) {
          setAssignableEmps(empData.map((e: any) => ({ emp_code: e.emp_code, emp_name: e.emp_name })))
        }
      } catch { /* emp list might not be available */ }
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { detail?: string }; status?: number } }
        setError('Error: ' + JSON.stringify(axErr.response?.data?.detail || axErr.response?.status))
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load task')
      }
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { fetchTask() }, [fetchTask])

  const tsi = task?.tsi
  const progress = task?.progress || []
  const documents = task?.documents || []
  const events = task?.events || []
  const filters = task?.filters || []
  const activeL3 = findActiveL3(progress)
  const hasDocuments = documents.length > 0
  const isLF240 = progress.some(l1 => l1.tst_id?.startsWith('TST-034') || l1.tst_name?.toLowerCase().includes('contract'))
  const isInProgress = tsi?.status === 'IN_PROGRESS'

  const handleInlineAction = async (node: ProgressNode) => {
    const state = reviewState[node.tsi_id]
    if (!state?.action) return
    setSavingId(node.tsi_id)
    setActionMsg(null)
    try {
      if (state.action === 'APPROVED') {
        await api.post(`/api/legal/task/${node.tsi_id}/approve`)
      } else if (state.action === 'REJECTED') {
        await api.post(`/api/legal/task/${node.tsi_id}/reject`, { reason: state.comment || 'Rejected by admin' })
      }
      setActionMsg(`Step ${node.tst_name} ${state.action.toLowerCase()} successfully`)
      setReviewState((prev) => { const copy = { ...prev }; delete copy[node.tsi_id]; return copy })
      await fetchTask()
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { message?: string } } }
        setActionMsg('Error: ' + (axErr.response?.data?.message || 'Action failed'))
      } else { setActionMsg('Error: Action failed') }
    } finally { setSavingId(null) }
  }

  const handleUserSubmit = async () => {
    if (!activeL3) return
    setActionLoading(true)
    setActionMsg(null)
    try {
      await api.post(`/api/legal/task/${activeL3.tsi_id}/approve`)
      setActionMsg('Step submitted to review')
      try { await api.post(`/api/legal/task/${activeL3.tsi_id}/ai-review`) } catch { /* optional */ }
      await fetchTask()
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { message?: string } } }
        setActionMsg('Error: ' + (axErr.response?.data?.message || 'Submit failed'))
      } else { setActionMsg('Error: Submit failed') }
    } finally { setActionLoading(false) }
  }

  const handleResubmit = async () => {
    if (!activeL3) return
    setActionLoading(true)
    setActionMsg(null)
    try {
      await api.post(`/api/legal/task/${activeL3.tsi_id}/approve`)
      setActionMsg('Step re-submitted')
      try { await api.post(`/api/legal/task/${activeL3.tsi_id}/ai-review`) } catch { /* optional */ }
      await fetchTask()
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { message?: string } } }
        setActionMsg('Error: ' + (axErr.response?.data?.message || 'Resubmit failed'))
      } else { setActionMsg('Error: Resubmit failed') }
    } finally { setActionLoading(false) }
  }

  const handleUpload = async () => {
    if (!activeL3) return

    // Check if we have a real file selected or just a URL
    const selectedFile = fileInputRef.current?.files?.[0]

    if (selectedFile) {
      // Real file upload via multipart form
      setActionLoading(true)
      setActionMsg(null)
      try {
        const formData = new FormData()
        formData.append('file', selectedFile)
        formData.append('tdt_id', 'TDT-001')
        await api.post(`/api/legal/task/${activeL3.tsi_id}/upload-file`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        setActionMsg('File uploaded successfully')
        setUploadFileName('')
        setUploadFileUrl('')
        setShowUpload(false)
        if (fileInputRef.current) fileInputRef.current.value = ''
        await fetchTask()
      } catch (err: unknown) {
        if (err && typeof err === 'object' && 'response' in err) {
          const axErr = err as { response?: { data?: { message?: string } } }
          setActionMsg('Error: ' + (axErr.response?.data?.message || 'Upload failed'))
        } else { setActionMsg('Error: Upload failed') }
      } finally { setActionLoading(false) }
    } else if (uploadFileUrl.trim()) {
      // URL-based upload
      setActionLoading(true)
      setActionMsg(null)
      try {
        await api.post(`/api/legal/task/${activeL3.tsi_id}/document`, {
          tdt_id: 'TDT-001',
          file_name: uploadFileName.trim() || 'document',
          file_url: uploadFileUrl.trim(),
        })
        setActionMsg('Document link saved')
        setUploadFileName('')
        setUploadFileUrl('')
        setShowUpload(false)
        await fetchTask()
      } catch (err: unknown) {
        if (err && typeof err === 'object' && 'response' in err) {
          const axErr = err as { response?: { data?: { message?: string } } }
          setActionMsg('Error: ' + (axErr.response?.data?.message || 'Upload failed'))
        } else { setActionMsg('Error: Upload failed') }
      } finally { setActionLoading(false) }
    } else {
      setActionMsg('Please select a file or enter a URL')
    }
  }

  const handleDeleteDoc = async (doc: Document) => {
    const docId = doc.tdi_id || doc.id
    const docTsiId = doc.tsi_id || activeL3?.tsi_id
    if (!docId || !docTsiId) return
    if (!window.confirm(`Delete "${doc.file_name}"?`)) return
    setActionMsg(null)
    try {
      await api.delete(`/api/legal/task/${docTsiId}/document/${docId}`)
      setActionMsg('Document deleted')
      await fetchTask()
    } catch { setActionMsg('Error: Delete failed') }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploadFileName(file.name)
      setUploadFileUrl(`uploads/${file.name}`)
    }
  }

  const handleAiCheck = async () => {
    if (!activeL3) return
    setAiChecking(true)
    setAiCheckResult(null)
    setActionMsg(null)
    try {
      const res = await api.post(`/api/legal/task/${activeL3.tsi_id}/ai-review`)
      setAiCheckResult(res.data?.data || res.data)
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { message?: string } } }
        setActionMsg('AI Check Error: ' + (axErr.response?.data?.message || 'Failed'))
      } else { setActionMsg('AI Check Error: Failed') }
    } finally { setAiChecking(false) }
  }

  const triggerAiReview = async (tsiId: string) => {
    setAiReviewingId(tsiId)
    setActionMsg(null)
    try {
      await api.post(`/api/legal/task/${tsiId}/ai-review`)
      setActionMsg('AI review completed')
      await fetchTask()
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { message?: string } } }
        setActionMsg('AI Review Error: ' + (axErr.response?.data?.message || 'Failed'))
      } else { setActionMsg('AI Review Error: Failed') }
    } finally { setAiReviewingId(null) }
  }

  const handleSaveMeta = async () => {
    if (!id) return
    setSavingMeta(true)
    setActionMsg(null)
    try {
      await api.put(`/api/legal/task/${id}/metadata`, lf240Meta)
      setActionMsg('Thông tin bổ sung đã lưu')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { message?: string } } }
        setActionMsg('Error: ' + (axErr.response?.data?.message || 'Save failed'))
      } else { setActionMsg('Error: Save failed') }
    } finally { setSavingMeta(false) }
  }

  const handleReassign = async (newEmpCode: string) => {
    if (!id || !newEmpCode) return
    setReassigning(true)
    setActionMsg(null)
    try {
      await api.put(`/api/legal/task/${id}/reassign`, { new_emp_code: newEmpCode })
      setActionMsg('Task đã được chuyển giao')
      await fetchTask()
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { data?: { message?: string } } }
        setActionMsg('Error: ' + (axErr.response?.data?.message || 'Reassign failed'))
      } else { setActionMsg('Error: Reassign failed') }
    } finally { setReassigning(false) }
  }

  if (loading) return <div data-testid="loading-state" className="text-gray-500 p-8">Loading task...</div>

  if (error || !task) return (
    <div className="p-8">
      <button className="mb-4 text-blue-600 hover:underline text-sm" onClick={() => navigate(-1)}>&larr; Back</button>
      <div className="bg-red-50 text-red-700 p-4 rounded">{error || 'Task not found'}</div>
    </div>
  )

  return (
    <div data-testid="task-detail-page" className="space-y-6">
      {/* 1. Back button */}
      <button className="text-blue-600 hover:underline text-sm flex items-center gap-1" onClick={() => navigate(-1)}>
        &larr; Back to Tasks
      </button>

      {/* 2. Status banners */}
      {tsi?.status === 'COMPLETED' && (
        <div className="bg-green-50 border border-green-200 text-green-800 p-4 rounded-lg text-center font-medium">
          ✅ This task has been completed
        </div>
      )}

      {/* 3. Action message feedback */}
      {actionMsg && (
        <div className={`p-3 rounded text-sm ${actionMsg.startsWith('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
          {actionMsg}
          <button className="ml-3 text-xs underline" onClick={() => setActionMsg(null)}>dismiss</button>
        </div>
      )}

      {/* 4. Task Info Header */}
      <div data-testid="task-info-header" className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold">{tsi?.title || 'Untitled Task'}</h2>
            <p className="text-sm text-gray-500 font-mono mt-1">{tsi?.tsi_code || tsi?.tsi_id}</p>
          </div>
          <span className={`px-3 py-1 rounded text-sm font-medium ${STATUS_COLORS[tsi?.status || ''] || 'bg-gray-100'}`}>
            {tsi?.status}
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div><span className="text-gray-500">Priority:</span> <span className="font-medium">{tsi?.priority || '-'}</span></div>
          <div><span className="text-gray-500">Due Date:</span> <span className="font-medium">{tsi?.due_date || '-'}</span></div>
          <div>
            <span className="text-gray-500">Assigned To:</span>{' '}
            {isAdmin && assignableEmps.length > 0 ? (
              <select className="border rounded px-2 py-1 text-sm font-medium" value={tsi?.assigned_to || ''}
                onChange={(e) => handleReassign(e.target.value)} disabled={reassigning}>
                <option value="">-- Select --</option>
                {assignableEmps.map(emp => (
                  <option key={emp.emp_code} value={emp.emp_code}>{emp.emp_name} ({emp.emp_code})</option>
                ))}
              </select>
            ) : (
              <span className="font-medium">{tsi?.assigned_to || '-'}</span>
            )}
            {reassigning && <span className="text-xs text-gray-400 ml-2">Đang chuyển...</span>}
          </div>
          <div><span className="text-gray-500">Created At:</span> <span className="font-medium">{tsi?.created_at ? new Date(tsi.created_at).toLocaleDateString() : '-'}</span></div>
        </div>
        {filters.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {filters.map((f, i) => (
              <span key={i} className="bg-indigo-50 text-indigo-700 px-2 py-1 rounded text-xs font-medium">
                {f.filter_type}: {f.filter_code}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 5. Progress Tree */}
      <div data-testid="progress-tree-section" className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Progress Tree</h3>
        {progress.map((l1) => (
          <div key={l1.tsi_id} className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">{statusIcon(l1.status)}</span>
              <span className="font-semibold text-base">{l1.tst_name}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[l1.status] || 'bg-gray-100'}`}>{l1.status}</span>
            </div>
            {(l1.children || []).map((l2) => (
              <div key={l2.tsi_id} className="ml-6 mb-4 border-l-4 border-blue-300 pl-4">
                <div className="flex items-center gap-2 mb-2">
                  <span>{statusIcon(l2.status)}</span>
                  <span className="font-medium text-sm">{l2.tst_name}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[l2.status] || 'bg-gray-100'}`}>{l2.status}</span>
                </div>
                {(l2.children || []).length > 0 && (
                  <div className="ml-4 overflow-x-auto">
                    <table className="w-full text-sm border rounded table-fixed">
                      <thead>
                        <tr className="bg-gray-50 border-b">
                          <th className="text-left p-2 w-8">#</th>
                          <th className="text-left p-2" style={{width:'50%'}}>Step</th>
                          <th className="text-left p-2 w-28">Status</th>
                          <th className="text-left p-2" style={{width:'25%'}}>Comment</th>
                          {isAdmin && <th className="text-left p-2 w-16">Action</th>}
                        </tr>
                      </thead>
                      <tbody>
                        {(l2.children || []).map((l3, idx) => {
                          const isDone = ['APPROVED', 'COMPLETED', 'REJECTED', 'SUBMITTED'].includes(l3.status)
                          const rs = reviewState[l3.tsi_id] || { action: '', comment: '' }
                          return (
                            <>
                              <tr key={l3.tsi_id} className="border-b hover:bg-gray-50">
                                <td className="p-2 text-gray-500">{idx + 1}</td>
                                <td className="p-2"><span className="mr-1">{statusIcon(l3.status)}</span>{l3.tst_name}</td>
                                <td className="p-2">
                                  {isDone ? (
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[l3.status] || 'bg-gray-100'}`}>{l3.status}</span>
                                  ) : isAdmin && !isDone ? (
                                    <select className="border rounded px-2 py-1 text-xs" value={rs.action}
                                      onChange={(e) => setReviewState((prev) => ({ ...prev, [l3.tsi_id]: { ...prev[l3.tsi_id], action: e.target.value, comment: prev[l3.tsi_id]?.comment || '' } }))}>
                                      <option value="">-- Select --</option>
                                      <option value="APPROVED">Approved</option>
                                      <option value="REJECTED">Reject</option>
                                    </select>
                                  ) : (
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[l3.status] || 'bg-gray-100'}`}>{l3.status}</span>
                                  )}
                                </td>
                                <td className="p-2 text-xs text-gray-600">
                                  {isDone ? (l3.comment || '-') : isAdmin && !isDone ? (
                                    <input type="text" className="border rounded px-2 py-1 text-xs w-full" placeholder="Comment..."
                                      value={rs.comment} onChange={(e) => setReviewState((prev) => ({ ...prev, [l3.tsi_id]: { ...prev[l3.tsi_id], action: prev[l3.tsi_id]?.action || '', comment: e.target.value } }))} />
                                  ) : '-'}
                                </td>
                                {isAdmin && (
                                  <td className="p-2">
                                    {!isDone && rs.action && (
                                      <button className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 disabled:opacity-50"
                                        disabled={savingId === l3.tsi_id} onClick={() => handleInlineAction(l3)}>
                                        {savingId === l3.tsi_id ? 'Saving...' : 'Save'}
                                      </button>
                                    )}
                                  </td>
                                )}
                              </tr>
                              {l3.ai_review && (
                                <tr key={`${l3.tsi_id}-ai`} className="border-b">
                                  <td colSpan={isAdmin ? 5 : 4} className="p-2">
                                    <button className={`text-xs px-2 py-1 rounded font-medium ${l3.ai_review.verdict === 'PASS' ? 'bg-green-100 text-green-800' : l3.ai_review.verdict === 'PASS_WITH_NOTES' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}
                                      onClick={() => setExpandedAiReview((prev) => ({ ...prev, [l3.tsi_id]: !prev[l3.tsi_id] }))}>
                                      🤖 AI: {l3.ai_review.verdict} (Score: {l3.ai_review.score}){expandedAiReview[l3.tsi_id] ? ' ▲' : ' ▼'}
                                    </button>
                                    {expandedAiReview[l3.tsi_id] && (
                                      <div className="mt-2 bg-gray-50 rounded p-3 text-xs space-y-2">
                                        <p><strong>Summary:</strong> {l3.ai_review.summary}</p>
                                        {l3.ai_review.checklist?.length > 0 && (
                                          <div>
                                            <strong>Checklist:</strong>
                                            <ul className="mt-1 space-y-1">
                                              {l3.ai_review.checklist.map((c, ci) => (
                                                <li key={ci} className="flex items-start gap-1">
                                                  <span>{c.status === 'pass' ? '✅' : '❌'}</span>
                                                  <span>{c.item}{c.note && <span className="text-gray-500 ml-1">— {c.note}</span>}</span>
                                                </li>
                                              ))}
                                            </ul>
                                          </div>
                                        )}
                                        {l3.ai_review.docs_reviewed?.length > 0 && (
                                          <p><strong>Docs reviewed:</strong> {l3.ai_review.docs_reviewed.join(', ')}</p>
                                        )}
                                        <p className="text-gray-400">Model: {l3.ai_review.model}</p>
                                      </div>
                                    )}
                                  </td>
                                </tr>
                              )}
                              {isAdmin && l3.status === 'SUBMITTED' && !l3.ai_review && (
                                <tr key={`${l3.tsi_id}-ai-btn`} className="border-b">
                                  <td colSpan={isAdmin ? 5 : 4} className="p-2">
                                    <button className="text-xs bg-indigo-100 text-indigo-700 px-3 py-1 rounded hover:bg-indigo-200 disabled:opacity-50"
                                      disabled={aiReviewingId === l3.tsi_id} onClick={() => triggerAiReview(l3.tsi_id)}>
                                      {aiReviewingId === l3.tsi_id ? '🤖 Running AI Review...' : '🤖 Run AI Review'}
                                    </button>
                                  </td>
                                </tr>
                              )}
                            </>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* 5.5 LF240 Additional Fields */}
      {isLF240 && isInProgress && (
        <div data-testid="lf240-fields" className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Thông tin bổ sung — Hợp đồng đối tác</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SĐT người đề xuất <span className="text-red-500">*</span></label>
              <input type="tel" className="w-full border rounded px-3 py-2 text-sm" placeholder="+84-xxx-xxx-xxx"
                value={lf240Meta.requester_phone || ''} onChange={(e) => setLf240Meta(prev => ({...prev, requester_phone: e.target.value}))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email quản lý người đề xuất <span className="text-red-500">*</span></label>
              <input type="email" className="w-full border rounded px-3 py-2 text-sm" placeholder="manager@apero.vn"
                value={lf240Meta.manager_email || ''} onChange={(e) => setLf240Meta(prev => ({...prev, manager_email: e.target.value}))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SĐT đối tác</label>
              <input type="tel" className="w-full border rounded px-3 py-2 text-sm" placeholder="+84-xxx-xxx-xxx"
                value={lf240Meta.partner_phone || ''} onChange={(e) => setLf240Meta(prev => ({...prev, partner_phone: e.target.value}))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mail liên hệ đối tác <span className="text-red-500">*</span></label>
              <input type="email" className="w-full border rounded px-3 py-2 text-sm" placeholder="contact@partner.com"
                value={lf240Meta.partner_contact_email || ''} onChange={(e) => setLf240Meta(prev => ({...prev, partner_contact_email: e.target.value}))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mail ký hợp đồng đối tác</label>
              <input type="email" className="w-full border rounded px-3 py-2 text-sm" placeholder="contract@partner.com"
                value={lf240Meta.partner_contract_email || ''} onChange={(e) => setLf240Meta(prev => ({...prev, partner_contract_email: e.target.value}))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mã PE <span className="text-red-500">*</span></label>
              <input type="text" className="w-full border rounded px-3 py-2 text-sm" placeholder="PE-2026-001"
                value={lf240Meta.pe_code || ''} onChange={(e) => setLf240Meta(prev => ({...prev, pe_code: e.target.value}))} />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Mục đích ký kết / ban hành <span className="text-red-500">*</span></label>
              <textarea className="w-full border rounded px-3 py-2 text-sm" rows={3} placeholder="Mô tả mục đích ký kết hợp đồng..."
                value={lf240Meta.purpose || ''} onChange={(e) => setLf240Meta(prev => ({...prev, purpose: e.target.value}))} />
            </div>
          </div>
          <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium disabled:opacity-50"
            disabled={savingMeta} onClick={handleSaveMeta}>
            {savingMeta ? 'Đang lưu...' : 'Lưu thông tin bổ sung'}
          </button>
        </div>
      )}

      {/* 6. Documents Table */}
      <div data-testid="documents-section" className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Documents ({documents.length})</h3>
        {documents.length > 0 ? (
          <table className="w-full text-sm border rounded table-fixed">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="text-left p-2">File Name</th>
                <th className="text-left p-2">Version</th>
                <th className="text-left p-2">Uploaded By</th>
                <th className="text-left p-2">Uploaded At</th>
                <th className="text-left p-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc, i) => (
                <tr key={doc.tdi_id || doc.id || i} className="border-b">
                  <td className="p-2">{doc.file_name}</td>
                  <td className="p-2">{doc.version || 1}</td>
                  <td className="p-2 text-xs">{doc.uploaded_by || '-'}</td>
                  <td className="p-2 text-xs">{doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleString() : '-'}</td>
                  <td className="p-2 flex items-center gap-2">
                    {doc.file_url && (
                      <>
                        <a href={resolveFileUrl(doc.file_url)} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-xs">View</a>
                        <a href={resolveFileUrl(doc.file_url)} download className="text-green-600 hover:underline text-xs">Download</a>
                      </>
                    )}
                    {!isAdmin && tsi?.status !== 'COMPLETED' && (
                      <button className="text-red-500 hover:text-red-700 text-xs ml-2" onClick={() => handleDeleteDoc(doc)} title="Delete document">✕</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="text-gray-400 text-sm">No documents uploaded yet.</p>}
      </div>

      {/* 8. User Actions */}
      {!isAdmin && tsi?.status !== 'COMPLETED' && activeL3 && (
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h3 className="text-lg font-semibold">Actions</h3>
          <div className="text-sm bg-blue-50 text-blue-800 px-3 py-2 rounded">
            Active Step: <strong>{activeL3.tst_name}</strong> ({activeL3.status})
          </div>
          {!hasDocuments && (
            <div className="text-sm bg-amber-50 text-amber-800 px-3 py-2 rounded">
              ⚠️ No documents uploaded. Please upload at least one document before submitting.
            </div>
          )}
          <div className="flex flex-wrap gap-3">
            <button className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm font-medium" onClick={() => setShowUpload(!showUpload)}>
              📄 Upload Document
            </button>
            <button className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm font-medium disabled:opacity-50"
              disabled={aiChecking || !hasDocuments} onClick={handleAiCheck}>
              {aiChecking ? '🤖 Checking...' : '🤖 AI Check'}
            </button>
            {activeL3.status === 'REJECTED' ? (
              <button className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 text-sm font-medium disabled:opacity-50"
                disabled={actionLoading} onClick={handleResubmit}>
                {actionLoading ? 'Re-submitting...' : '🔄 Re-submit'}
              </button>
            ) : (
              <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium disabled:opacity-50"
                disabled={actionLoading} onClick={handleUserSubmit}>
                {actionLoading ? 'Submitting...' : '📤 Submit to Review'}
              </button>
            )}
          </div>

          {aiCheckResult && (
            <div className="border rounded-lg p-4 bg-gray-50 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm">🤖 AI Check Result</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${aiCheckResult.verdict === 'PASS' ? 'bg-green-100 text-green-800' : aiCheckResult.verdict === 'PASS_WITH_NOTES' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                    {aiCheckResult.verdict} (Score: {aiCheckResult.score})
                  </span>
                </div>
                <button className="text-gray-400 hover:text-gray-600 text-sm" onClick={() => setAiCheckResult(null)}>✕ Close</button>
              </div>
              <p className="text-sm text-gray-700">{aiCheckResult.summary}</p>
              {aiCheckResult.checklist?.length > 0 && (
                <div className="text-sm">
                  <strong>Checklist:</strong>
                  <ul className="mt-1 space-y-1">
                    {aiCheckResult.checklist.map((c, ci) => (
                      <li key={ci} className="flex items-start gap-1">
                        <span>{c.status === 'pass' ? '✅' : '❌'}</span>
                        <span>{c.item}{c.note && <span className="text-gray-500 ml-1">— {c.note}</span>}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <p className="text-xs text-gray-400">Model: {aiCheckResult.model}</p>
            </div>
          )}

          {showUpload && (
            <div className="border rounded-lg p-4 bg-gray-50 space-y-3">
              <h4 className="font-medium text-sm">Upload Document</h4>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Select File ({ACCEPTED_FILE_TYPES})</label>
                <input ref={fileInputRef} type="file" accept={ACCEPTED_FILE_TYPES} className="text-sm" onChange={handleFileSelect} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Or enter file URL directly</label>
                <input type="text" className="w-full border rounded px-3 py-2 text-sm" placeholder="https://example.com/document.pdf"
                  value={uploadFileUrl} onChange={(e) => setUploadFileUrl(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">File Name</label>
                <input type="text" className="w-full border rounded px-3 py-2 text-sm" placeholder="document.pdf"
                  value={uploadFileName} onChange={(e) => setUploadFileName(e.target.value)} />
              </div>
              <div className="flex gap-2">
                <button className="px-4 py-2 bg-purple-600 text-white rounded text-sm hover:bg-purple-700 disabled:opacity-50"
                  disabled={actionLoading || !uploadFileName.trim() || !uploadFileUrl.trim()} onClick={handleUpload}>
                  {actionLoading ? 'Uploading...' : 'Submit'}
                </button>
                <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
                  onClick={() => { setShowUpload(false); setUploadFileName(''); setUploadFileUrl('') }}>Cancel</button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 9. Admin Upload */}
      {isAdmin && tsi?.status !== 'COMPLETED' && activeL3 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="text-sm font-semibold mb-2">Admin: Upload Document</h4>
          <div className="flex flex-wrap gap-2 items-end">
            <div>
              <label className="block text-xs text-gray-600 mb-1">File</label>
              <input ref={fileInputRef} type="file" accept={ACCEPTED_FILE_TYPES} className="text-xs" onChange={handleFileSelect} />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs text-gray-600 mb-1">URL</label>
              <input type="text" className="w-full border rounded px-2 py-1 text-xs" placeholder="File URL"
                value={uploadFileUrl} onChange={(e) => setUploadFileUrl(e.target.value)} />
            </div>
            <div className="flex-1 min-w-[150px]">
              <label className="block text-xs text-gray-600 mb-1">Name</label>
              <input type="text" className="w-full border rounded px-2 py-1 text-xs" placeholder="File name"
                value={uploadFileName} onChange={(e) => setUploadFileName(e.target.value)} />
            </div>
            <button className="px-3 py-1 bg-purple-600 text-white rounded text-xs hover:bg-purple-700 disabled:opacity-50"
              disabled={actionLoading || !uploadFileName.trim() || !uploadFileUrl.trim()} onClick={handleUpload}>
              {actionLoading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </div>
      )}

      {/* 7. Event Log (collapsible) — moved to bottom */}
      <div data-testid="event-log-section" className="bg-white rounded-lg shadow p-6">
        <button className="text-lg font-semibold flex items-center gap-2" onClick={() => setShowEventLog(!showEventLog)}>
          Event Log ({events.length}) <span className="text-sm">{showEventLog ? '▲' : '▼'}</span>
        </button>
        {showEventLog && (
          <div className="mt-4 space-y-3">
            {events.length > 0 ? events.map((ev, i) => (
              <div key={ev.id || i} className="flex items-start gap-3 border-l-4 border-gray-200 pl-3 py-1">
                <span className={`px-2 py-0.5 rounded text-xs font-medium whitespace-nowrap ${EVENT_COLORS[ev.event_type || ''] || 'bg-gray-100 text-gray-800'}`}>{ev.event_type}</span>
                <div className="text-xs text-gray-600 flex-1">
                  <span className="font-medium">{ev.emp_id || 'SYSTEM'}</span>
                  {ev.event_data && <span className="ml-2 text-gray-500">{ev.event_data.length > 100 ? ev.event_data.slice(0, 100) + '...' : ev.event_data}</span>}
                </div>
                <span className="text-xs text-gray-400 whitespace-nowrap">{ev.created_at ? new Date(ev.created_at).toLocaleString() : '-'}</span>
              </div>
            )) : <p className="text-gray-400 text-sm">No events recorded.</p>}
          </div>
        )}
      </div>
    </div>
  )
}
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/auth.store'
import api from '../services/api'

const CID = '21672960606-1ksk32rpsm8sga0enpt44ul3bhnbhrm5.apps.googleusercontent.com'

const DEVS = [
  { email: 'trangph@apero.vn', label: 'TrangPH', sec: 'SEC1', desc: 'User - MyPT - MyCDT', grad: 'from-blue-500 to-blue-700', bg: 'bg-blue-500' },
  { email: 'oainv@apero.vn', label: 'OaiNV', sec: 'SEC2', desc: 'Trainer - AllPT - CDTParent', grad: 'from-amber-500 to-amber-700', bg: 'bg-amber-500' },
  { email: 'giangpnt@apero.vn', label: 'GiangPNT', sec: 'SEC3', desc: 'Manager - AllPT - MyCDT', grad: 'from-purple-500 to-purple-700', bg: 'bg-purple-500' },
  { email: 'hoangdnh@apero.vn', label: 'HoangDNH', sec: 'SEC4', desc: 'Admin - AllPT - AllCDT', grad: 'from-emerald-500 to-emerald-700', bg: 'bg-emerald-500' },
]

declare global { interface Window { google: any } }

export function LoginPage() {
  const nav = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [dev, setDev] = useState(false)
  const gRef = useRef<HTMLDivElement>(null)

  const done = (d: any) => {
    const { token, user: u } = d
    // Admin = SEC4 OR has Approver/Checker role_legal (can review and approve tasks)
    const isAdminUser = u.empsec === 'SEC4' || u.role_legal === 'Approver' || u.role_legal === 'Checker'
    setAuth(token, {
      emp_code: u.emp_code, emp_name: u.emp_name,
      role: isAdminUser ? 'ADMIN' : 'PRODUCT_MANAGER',
      empsec: u.empsec, pt_allowed: u.pt_allowed, cdt_allowed: u.cdt_allowed,
      krf_level: u.krf_level, cdt_1: u.cdt_1, role_legal: u.role_legal, google_email: u.google_email,
    })
    nav('/legal')
  }

  useEffect(() => {
    const init = () => {
      if (!window.google || !gRef.current) return
      window.google.accounts.id.initialize({
        client_id: CID,
        callback: async (r: any) => {
          setBusy(true); setErr('')
          try { const res = await api.post('/api/auth/login', { google_token: r.credential }); done(res.data.data) }
          catch (e: any) { setErr(e?.response?.data?.message === 'Employee not found' ? 'Account not registered.' : (e?.response?.data?.message || 'Login failed')) }
          finally { setBusy(false) }
        },
      })
      window.google.accounts.id.renderButton(gRef.current, { theme: 'outline', size: 'large', width: 320, text: 'signin_with', shape: 'pill' })
    }
    if (window.google) init()
    else { const t = setInterval(() => { if (window.google) { clearInterval(t); init() } }, 100); return () => clearInterval(t) }
  }, [])

  const devLogin = async (email: string) => {
    setBusy(true); setErr('')
    try { const r = await api.post('/api/auth/login', { email }); done(r.data.data) }
    catch (e: any) { setErr(e?.response?.data?.message || 'Login failed') }
    finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 flex items-center justify-center px-4 relative overflow-hidden">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-blue-500/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-emerald-500/5 rounded-full blur-3xl" />
      <div className="relative z-10 w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 shadow-lg shadow-blue-500/25 mb-4">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Legal Workflow</h1>
          <p className="text-sm text-gray-500 mt-1">Apero Group &#183; Permission System</p>
        </div>
        <div className="bg-gray-900/80 backdrop-blur-xl border border-gray-800/50 rounded-2xl p-6 shadow-2xl">
          {err && (
            <div className="mb-4 flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
              <span className="text-red-400 text-sm">&#x2716;</span>
              <p className="text-sm text-red-300">{err}</p>
            </div>
          )}
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-3 font-medium text-center">Sign in with your company account</p>
          <div className="flex justify-center"><div ref={gRef} className="min-h-[44px]" /></div>
          {busy && (
            <div className="flex items-center justify-center gap-2 mt-4">
              <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-gray-400">Authenticating...</span>
            </div>
          )}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-800" /></div>
            <div className="relative flex justify-center">
              <button onClick={() => setDev(!dev)} className="px-3 py-1 bg-gray-900 text-[10px] text-gray-600 hover:text-gray-400 uppercase tracking-widest transition-colors">
                {dev ? '&#9662; Dev Mode' : '&#9656; Dev Mode'}
              </button>
            </div>
          </div>
          {dev && (
            <div className="space-y-2">
              {DEVS.map((u) => (
                <button key={u.email} onClick={() => devLogin(u.email)} disabled={busy}
                  data-testid={`login-${u.email.split('@')[0]}`}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl bg-gray-800/50 border border-gray-700/50 hover:border-gray-600 hover:bg-gray-800 transition-all disabled:opacity-40 group">
                  <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${u.grad} flex items-center justify-center text-white text-xs font-bold shadow-sm`}>{u.label[0]}</div>
                  <div className="flex-1 text-left">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-200 font-medium">{u.label}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold text-white ${u.bg}`}>{u.sec}</span>
                    </div>
                    <p className="text-[11px] text-gray-500">{u.desc}</p>
                  </div>
                  <span className="text-gray-600 group-hover:text-gray-400 transition-colors">&#8250;</span>
                </button>
              ))}
            </div>
          )}
        </div>
        <p className="text-center text-[10px] text-gray-700 mt-4">SEC Permission System v1.0 &#183; Powered by BigQuery</p>
      </div>
    </div>
  )
}

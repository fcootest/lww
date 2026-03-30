import { create } from 'zustand'

export interface User {
  emp_code: string
  role: string
  emp_name: string
  // SEC permission fields
  empsec?: string
  pt_allowed?: string
  cdt_allowed?: string
  krf_level?: number
  cdt_1?: string
  role_legal?: string
  google_email?: string
}

interface AuthState {
  token: string | null
  user: User | null
  setAuth: (token: string, user: User) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  setAuth: (token, user) => set({ token, user }),
  clearAuth: () => set({ token: null, user: null }),
}))

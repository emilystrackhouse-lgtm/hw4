import { createContext, useContext } from 'react'
import type { User } from './api.ts'

export type AuthControls = {
  user: User | null
  // True until the first "who am I" check finishes, so pages don't flash the wrong state.
  checking: boolean
  setUser: (user: User | null) => void
  signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthControls | null>(null)

export function useAuth() {
  const controls = useContext(AuthContext)
  if (!controls) throw new Error('useAuth must be used inside AuthProvider')
  return controls
}

export function formatMemberSince(createdAt: string) {
  // SQLite stores UTC as "YYYY-MM-DD HH:MM:SS".
  const date = new Date(`${createdAt.replace(' ', 'T')}Z`)
  return Number.isNaN(date.getTime())
    ? createdAt
    : date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

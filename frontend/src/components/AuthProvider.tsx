import { useEffect, useState, type ReactNode } from 'react'
import { fetchCurrentUser, logOut, type User } from '../api.ts'
import { AuthContext } from '../auth.ts'

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    fetchCurrentUser()
      .then(setUser, () => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  const signOut = async () => {
    try {
      await logOut()
    } finally {
      setUser(null)
    }
  }

  return <AuthContext.Provider value={{ user, checking, setUser, signOut }}>{children}</AuthContext.Provider>
}

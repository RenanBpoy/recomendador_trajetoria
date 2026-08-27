import { useEffect, useState } from 'react'
import { AUTH_CHANGED_EVENT, getStoredAuth } from '../services/auth'

export function useStoredAuth() {
  const [auth, setAuth] = useState(() => getStoredAuth())

  useEffect(() => {
    const refresh = () => setAuth(getStoredAuth())
    window.addEventListener(AUTH_CHANGED_EVENT, refresh)
    window.addEventListener('storage', refresh)
    return () => {
      window.removeEventListener(AUTH_CHANGED_EVENT, refresh)
      window.removeEventListener('storage', refresh)
    }
  }, [])

  return auth
}

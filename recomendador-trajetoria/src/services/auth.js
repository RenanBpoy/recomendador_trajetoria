import { apiPost } from './api'
import { clearSessionCache } from './sessionCache'

const AUTH_STORAGE_KEY = 'recomendador_trajetoria.auth'
export const AUTH_CHANGED_EVENT = 'recomendador-trajetoria:auth-changed'

function notifyAuthChanged() {
  if (typeof window !== 'undefined') window.dispatchEvent(new Event(AUTH_CHANGED_EVENT))
}

export function signup(data) {
  return apiPost('/autenticacao/cadastro', data)
}

export function login(data) {
  return apiPost('/autenticacao/login', data)
}

export function storeAuthSession(authData) {
  if (!authData?.sessao?.access_token) return false

  const expiresIn = Number(authData.sessao.expires_in) || 0
  clearSessionCache()
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({
    usuario: authData.usuario,
    perfil: authData.perfil,
    sessao: authData.sessao,
    expires_at: Date.now() + expiresIn * 1000,
  }))
  notifyAuthChanged()
  return true
}

export function getStoredAuth() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return null
    const stored = JSON.parse(raw)
    if (
      !stored?.sessao?.access_token
      || !stored?.perfil?.matricula
      || !stored?.perfil?.curso_codigo
    ) {
      clearAuthSession()
      return null
    }
    if (stored.expires_at && stored.expires_at <= Date.now()) {
      clearAuthSession()
      return null
    }
    return stored
  } catch {
    clearAuthSession()
    return null
  }
}

export function hasActiveSession() {
  return getStoredAuth() !== null
}

export function getAccessToken() {
  return getStoredAuth()?.sessao?.access_token || null
}

export function updateStoredProfile(profile) {
  const stored = getStoredAuth()
  if (!stored || !profile) return false
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({
    ...stored,
    perfil: { ...stored.perfil, ...profile },
  }))
  notifyAuthChanged()
  return true
}

export function updateStoredUser(user) {
  const stored = getStoredAuth()
  if (!stored || !user) return false
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({
    ...stored,
    usuario: { ...stored.usuario, ...user },
  }))
  notifyAuthChanged()
  return true
}

export function clearAuthSession() {
  const hadSession = localStorage.getItem(AUTH_STORAGE_KEY) !== null
  localStorage.removeItem(AUTH_STORAGE_KEY)
  clearSessionCache()
  if (hadSession) notifyAuthChanged()
}

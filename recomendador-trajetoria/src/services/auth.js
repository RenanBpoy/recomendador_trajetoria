import { apiPost } from './api'

const AUTH_STORAGE_KEY = 'recomendador_trajetoria.auth'

export function signup(data) {
  return apiPost('/autenticacao/cadastro', data)
}

export function login(data) {
  return apiPost('/autenticacao/login', data)
}

export function storeAuthSession(authData) {
  if (!authData?.sessao?.access_token) return false

  const expiresIn = Number(authData.sessao.expires_in) || 0
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({
    usuario: authData.usuario,
    perfil: authData.perfil,
    sessao: authData.sessao,
    expires_at: Date.now() + expiresIn * 1000,
  }))
  return true
}

export function getStoredAuth() {
  try {
    const stored = JSON.parse(localStorage.getItem(AUTH_STORAGE_KEY))
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

export function clearAuthSession() {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}

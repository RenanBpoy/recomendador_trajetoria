import { apiGet, apiPost } from './api'
import { clearSessionCache } from './sessionCache'

const AUTH_STORAGE_KEY = 'recomendador_trajetoria.auth'
const UFSM_ATTEMPT_KEY = 'recomendador_trajetoria.ufsm_attempt'
const UFSM_PORTAL_SIGNOUT_KEY = 'recomendador_trajetoria.ufsm_portal_signout'
export const AUTH_CHANGED_EVENT = 'recomendador-trajetoria:auth-changed'
let portalSignOutRequested = false

function notifyAuthChanged() {
  if (typeof window !== 'undefined') window.dispatchEvent(new Event(AUTH_CHANGED_EVENT))
}

export function signup(data) {
  return apiPost('/autenticacao/cadastro', data)
}

export function login(data) {
  return apiPost('/autenticacao/login', data)
}

export const getUfsmLoginConfiguration = () => apiGet('/autenticacao/ufsm/configuracao')

export function requestUfsmPortalSignOut() {
  portalSignOutRequested = true
  try {
    localStorage.setItem(UFSM_PORTAL_SIGNOUT_KEY, '1')
    sessionStorage.removeItem(UFSM_ATTEMPT_KEY)
  } catch {
    // A revogação da sessão local não depende do armazenamento do navegador.
  }
}

export function needsUfsmPortalSignOut() {
  try {
    return localStorage.getItem(UFSM_PORTAL_SIGNOUT_KEY) === '1' || portalSignOutRequested
  } catch {
    return portalSignOutRequested
  }
}

export function loginDestination(from) {
  return typeof from === 'string' && from.startsWith('/') && !from.startsWith('//') && !from.startsWith('/\\')
    && !['/login', '/cadastro', '/auth/callback'].includes(from.split(/[?#]/, 1)[0])
    ? from
    : '/home'
}

export async function beginUfsmLogin(from) {
  const result = await apiPost('/autenticacao/ufsm/iniciar', {})
  const portal = new URL(result.url)
  if (portal.protocol !== 'https:' || !result.tentativa) {
    throw new Error('O servidor não retornou um endereço válido para o login UFSM.')
  }
  sessionStorage.setItem(UFSM_ATTEMPT_KEY, JSON.stringify({
    tentativa: result.tentativa,
    destination: loginDestination(from),
  }))
  window.location.assign(portal.href)
}

export async function completeUfsmLogin() {
  const params = new URLSearchParams(window.location.search)
  window.history.replaceState(window.history.state, '', window.location.pathname)
  const attempt = JSON.parse(sessionStorage.getItem(UFSM_ATTEMPT_KEY))
  sessionStorage.removeItem(UFSM_ATTEMPT_KEY)
  if (params.has('error')) throw new Error('Não foi possível concluir a autorização na UFSM. Tente entrar novamente.')
  const code = params.get('code')
  if (!code || !attempt?.tentativa || params.getAll('code').length !== 1) {
    throw new Error('Nenhuma tentativa de login válida foi encontrada. Volte e entre novamente pela UFSM.')
  }
  const pending = await apiPost('/autenticacao/ufsm/callback', { code, tentativa: attempt.tentativa })
  if (!pending?.confirmacao || !pending.nome || !pending.vinculos?.length) {
    throw new Error('O servidor não retornou uma conta válida da UFSM.')
  }
  return { pending, destination: loginDestination(attempt.destination) }
}

export const confirmUfsmLogin = (confirmacao, vinculoId) => apiPost('/autenticacao/ufsm/confirmar', {
  confirmacao, vinculo_id: vinculoId,
})

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
  if (authData.sessao.access_token.startsWith('ufsm_')) {
    localStorage.removeItem(UFSM_PORTAL_SIGNOUT_KEY)
    portalSignOutRequested = false
  }
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

export async function signOut() {
  const token = getAccessToken()
  try {
    if (token?.startsWith('ufsm_')) {
      requestUfsmPortalSignOut()
      await apiPost('/autenticacao/ufsm/sair', undefined, token)
    }
  } finally {
    clearAuthSession()
  }
}

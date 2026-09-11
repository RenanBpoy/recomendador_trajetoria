import { apiGet } from './api'
import { getAccessToken, getStoredAuth } from './auth'
import { cachedSessionRequest, invalidateSessionCache } from './sessionCache'

const RECOMMENDATION_TTL = 5 * 60 * 1000
const GENERATED_RECOMMENDATION_PREFIX = 'recomendador_trajetoria.recommendation_generated.v1:'

function currentUserId() {
  const auth = getStoredAuth()
  return auth?.usuario?.id || auth?.perfil?.id || ''
}

export function hasGeneratedRecommendation(userId = currentUserId()) {
  if (!userId || typeof window === 'undefined') return false
  try {
    return window.localStorage.getItem(`${GENERATED_RECOMMENDATION_PREFIX}${userId}`) !== null
  } catch {
    return false
  }
}

function markRecommendationAsGenerated() {
  const userId = currentUserId()
  if (!userId || typeof window === 'undefined') return
  try {
    window.localStorage.setItem(
      `${GENERATED_RECOMMENDATION_PREFIX}${userId}`,
      new Date().toISOString(),
    )
  } catch {
    // A recomendação continua disponível na sessão atual mesmo sem persistência local.
  }
}

function cacheKey(ano, semestre) {
  const auth = getStoredAuth()
  const user = auth?.usuario?.id || auth?.perfil?.id || 'sem-usuario'
  const curriculum = auth?.perfil?.ppc_id || 'sem-ppc'
  return `${user}:recommendation:v3:${curriculum}:${ano || 'atual'}:${semestre || 'atual'}`
}

export function invalidateRecommendationCache() {
  const auth = getStoredAuth()
  const user = auth?.usuario?.id || auth?.perfil?.id || 'sem-usuario'
  invalidateSessionCache(`${user}:recommendation:`)
}

export function getCurrentRecommendation({ ano, semestre, force = false } = {}) {
  const query = ano && semestre ? `?ano=${ano}&semestre=${semestre}` : ''
  return cachedSessionRequest(
    cacheKey(ano, semestre),
    () => apiGet(`/recomendacoes/atual${query}`, getAccessToken()),
    { ttlMs: RECOMMENDATION_TTL, force },
  ).then((recommendation) => {
    markRecommendationAsGenerated()
    return recommendation
  })
}

export function getRecommendationContext({ ano, semestre, force = false } = {}) {
  const query = ano && semestre ? `?ano=${ano}&semestre=${semestre}` : ''
  return cachedSessionRequest(
    `${cacheKey(ano, semestre)}:context`,
    () => apiGet(`/recomendacoes/contexto${query}`, getAccessToken()),
    { ttlMs: RECOMMENDATION_TTL, force },
  )
}

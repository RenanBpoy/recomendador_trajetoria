import { apiGet } from './api'
import { getAccessToken, getStoredAuth } from './auth'
import { cachedSessionRequest, invalidateSessionCache } from './sessionCache'

const RECOMMENDATION_TTL = 5 * 60 * 1000

function cacheKey(ano, semestre) {
  const auth = getStoredAuth()
  const user = auth?.usuario?.id || auth?.perfil?.id || 'sem-usuario'
  const curriculum = auth?.perfil?.ppc_id || 'sem-ppc'
  return `${user}:recommendation:${curriculum}:${ano || 'atual'}:${semestre || 'atual'}`
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
  )
}

export function getRecommendationContext({ ano, semestre, force = false } = {}) {
  const query = ano && semestre ? `?ano=${ano}&semestre=${semestre}` : ''
  return cachedSessionRequest(
    `${cacheKey(ano, semestre)}:context`,
    () => apiGet(`/recomendacoes/contexto${query}`, getAccessToken()),
    { ttlMs: RECOMMENDATION_TTL, force },
  )
}

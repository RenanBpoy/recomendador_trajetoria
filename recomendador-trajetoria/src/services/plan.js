import { apiGet, apiPut } from './api'
import { getAccessToken, getStoredAuth } from './auth'
import { cachedSessionRequest, setSessionCache } from './sessionCache'

const PLAN_TTL = 10 * 60 * 1000

function cacheKey() {
  const auth = getStoredAuth()
  return `${auth?.usuario?.id || auth?.perfil?.id || 'sem-usuario'}:weekly-plan`
}

export function getWeeklyPlan({ force = false } = {}) {
  return cachedSessionRequest(
    cacheKey(),
    () => apiGet('/plano-semanal', getAccessToken()),
    { ttlMs: PLAN_TTL, force },
  )
}

export async function saveWeeklyPlan(items) {
  const saved = await apiPut('/plano-semanal', { itens: items }, getAccessToken())
  setSessionCache(cacheKey(), saved, PLAN_TTL)
  return saved
}

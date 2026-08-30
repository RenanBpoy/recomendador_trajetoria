import { apiGet, apiPost, apiPut } from './api'
import { getAccessToken, getStoredAuth } from './auth'
import { cachedSessionRequest, setSessionCache } from './sessionCache'
import { invalidateRecommendationCache } from './recommendation'

const QUESTIONNAIRE_TTL = 10 * 60 * 1000

function cacheKey() {
  const auth = getStoredAuth()
  return `${auth?.usuario?.id || auth?.perfil?.id || 'sem-usuario'}:current-questionnaire`
}

export function getCurrentQuestionnaire({ force = false } = {}) {
  return cachedSessionRequest(
    cacheKey(),
    () => apiGet('/questionarios/atual', getAccessToken()),
    { ttlMs: QUESTIONNAIRE_TTL, force },
  )
}

export async function saveQuestionnaireAnswer(questionId, value) {
  const questionnaire = await apiPut(
    `/questionarios/atual/respostas/${questionId}`,
    { valor: value },
    getAccessToken(),
  )
  setSessionCache(cacheKey(), questionnaire, QUESTIONNAIRE_TTL)
  invalidateRecommendationCache()
  return questionnaire
}

export async function completeCurrentQuestionnaire() {
  const questionnaire = await apiPost(
    '/questionarios/atual/concluir',
    undefined,
    getAccessToken(),
  )
  setSessionCache(cacheKey(), questionnaire, QUESTIONNAIRE_TTL)
  invalidateRecommendationCache()
  return questionnaire
}

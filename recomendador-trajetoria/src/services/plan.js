import { apiGet, apiPut } from './api'
import { getAccessToken, getStoredAuth } from './auth'
import { cachedSessionRequest, setSessionCache } from './sessionCache'
import { invalidateRecommendationCache } from './recommendation'

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

export async function saveWeeklyPlan(items, { invalidateRecommendation = true } = {}) {
  const saved = await apiPut('/plano-semanal', { itens: items }, getAccessToken())
  setSessionCache(cacheKey(), saved, PLAN_TTL)
  if (invalidateRecommendation) invalidateRecommendationCache()
  return saved
}

function planItemInput(item) {
  return {
    tipo_atividade: item.tipo_atividade,
    titulo: item.titulo,
    dia_semana: item.dia_semana,
    hora_inicio: item.hora_inicio,
    hora_fim: item.hora_fim,
    observacoes: item.observacoes || null,
  }
}

function itemKey(item) {
  return [
    item.tipo_atividade,
    String(item.titulo || '').trim().toLocaleUpperCase('pt-BR'),
    item.dia_semana,
    String(item.hora_inicio).slice(0, 5),
    String(item.hora_fim).slice(0, 5),
  ].join('|')
}

function recommendationItems(recommendation) {
  return (recommendation?.disciplinas || []).flatMap((discipline) => (
    discipline.horarios.map((schedule) => ({
      tipo_atividade: 'DISCIPLINA',
      titulo: discipline.disciplina_nome,
      dia_semana: schedule.dia_semana,
      hora_inicio: schedule.hora_inicio,
      hora_fim: schedule.hora_fim,
      observacoes: [
        discipline.oferta_disciplina_codigo || discipline.disciplina_codigo,
        `Turma ${discipline.codigo_turma}`,
        schedule.sala,
      ].filter(Boolean).join(' · '),
    }))
  ))
}

export async function applyRecommendationToWeeklyPlan(recommendation) {
  const current = (await getWeeklyPlan({ force: true })).map(planItemInput)
  const suggested = recommendationItems(recommendation)
  const existingKeys = new Set(current.map(itemKey))
  const added = suggested.filter((item) => {
    const key = itemKey(item)
    if (existingKeys.has(key)) return false
    existingKeys.add(key)
    return true
  })

  if (!added.length) {
    return { saved: current, addedMeetings: 0, addedDisciplines: 0 }
  }

  const saved = await saveWeeklyPlan(
    [...current, ...added],
    { invalidateRecommendation: false },
  )
  return {
    saved,
    addedMeetings: added.length,
    addedDisciplines: new Set(added.map((item) => item.titulo)).size,
  }
}

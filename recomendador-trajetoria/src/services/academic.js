import { academicPeriodCacheKey } from '../utils/academicPeriod'
import { apiDelete, apiGet, apiPatch, apiPut, apiUpload } from './api'
import { getAccessToken, getStoredAuth } from './auth'
import { cachedSessionRequest, invalidateSessionCache } from './sessionCache'
import { invalidateRecommendationCache } from './recommendation'

const CATALOG_TTL = 60 * 60 * 1000
const STUDENT_TTL = 10 * 60 * 1000

function academicScope() {
  const auth = getStoredAuth()
  return `${auth?.usuario?.id || auth?.perfil?.id || 'sem-usuario'}:academic:`
}

function cachedAcademicGet(key, path, { ttlMs = STUDENT_TTL, force = false, showLoading = true } = {}) {
  return cachedSessionRequest(
    `${academicScope()}${key}`,
    () => apiGet(path, getAccessToken(), { showLoading }),
    { ttlMs, force },
  )
}

export function invalidateAcademicCache() {
  invalidateSessionCache(academicScope())
  invalidateRecommendationCache()
}

export function getOfficialGrade(options = {}) {
  return cachedAcademicGet('ufsm:grade', '/autenticacao/ufsm/grade', options)
}

export function isInstitutionalSession(auth) {
  return Boolean(auth?.sessao?.access_token?.startsWith('ufsm_'))
}

function planSlotQuery(slot) {
  return new URLSearchParams({
    dia_semana: slot.dia_semana,
    hora_inicio: slot.hora_inicio,
    hora_fim: slot.hora_fim,
  })
}

export function listOtherPlanCourses() {
  return cachedAcademicGet(
    'ufsm:plano:catalogo-cursos',
    '/autenticacao/ufsm/plano/cursos',
    { showLoading: false, ttlMs: CATALOG_TTL },
  )
}

export function listInstitutionalPlanOfferings(slot, course) {
  const query = planSlotQuery(slot)
  if (course) query.set('curso_codigo', course)
  return cachedAcademicGet(
    `ufsm:plano:ofertas:${academicPeriodCacheKey()}:${query}`,
    `/autenticacao/ufsm/plano/ofertas?${query}`,
    { ttlMs: 300000, showLoading: false },
  )
}

export function listCourseCurricula(courseCode, options = {}) {
  return cachedAcademicGet(
    `curso:${courseCode}:ppcs`,
    `/cursos/${encodeURIComponent(courseCode)}/ppcs`,
    { ttlMs: CATALOG_TTL, ...options },
  )
}

export function listCurriculumComponents(curriculumId, options = {}) {
  return cachedAcademicGet(
    `ppc:${curriculumId}:componentes`,
    `/ppcs/${encodeURIComponent(curriculumId)}/componentes`,
    { ttlMs: CATALOG_TTL, ...options },
  )
}

export function getCurriculum(curriculumId, options = {}) {
  return cachedAcademicGet(
    `ppc:${curriculumId}`,
    `/ppcs/${encodeURIComponent(curriculumId)}`,
    { ttlMs: CATALOG_TTL, ...options },
  )
}

export function getSchoolHistory(registration, options = {}) {
  return cachedAcademicGet(
    `aluno:${registration}:historico`,
    `/alunos/${encodeURIComponent(registration)}/historico`,
    options,
  )
}

export function listNotApprovedDisciplines(registration, {
  ano,
  semestre,
  diaSemana,
  horaInicio,
  horaFim,
  force = false,
} = {}) {
  const query = new URLSearchParams({
    ano: String(ano),
    semestre: String(semestre),
    dia_semana: String(diaSemana),
    hora_inicio: horaInicio,
    hora_fim: horaFim,
  })
  return cachedAcademicGet(
    `aluno:${registration}:ofertas-nao-aprovadas:${query}`,
    `/alunos/${encodeURIComponent(registration)}/disciplinas-nao-aprovadas?${query}`,
    { force },
  )
}

export async function uploadSchoolHistory(file) {
  const result = await apiUpload('/historicos/importacoes', file, getAccessToken())
  invalidateAcademicCache()
  return result
}

export function getActiveHistoryImport(options = {}) {
  return cachedAcademicGet('historico:importacao-atual', '/historicos/importacoes/atual', options)
}

export async function reviewHistoryMatch(correspondenceId, action) {
  const result = await apiPatch(
    `/historicos/correspondencias/${encodeURIComponent(correspondenceId)}`,
    { acao: action },
    getAccessToken(),
  )
  invalidateAcademicCache()
  return result
}

export function listManualEquivalences(options = {}) {
  return cachedAcademicGet('historico:equivalencias-manuais', '/historicos/equivalencias-manuais', options)
}

export function listEquivalenceCandidates(componentId, options = {}) {
  return cachedAcademicGet(
    `componente:${componentId}:candidatos-equivalencia`,
    `/historicos/componentes/${encodeURIComponent(componentId)}/candidatos-equivalencia`,
    options,
  )
}

export async function saveManualEquivalence(componentId, slotOrder, historyItemId) {
  const result = await apiPut(
    `/historicos/componentes/${encodeURIComponent(componentId)}/vagas/${encodeURIComponent(slotOrder)}/equivalencia`,
    { historico_item_id: historyItemId },
    getAccessToken(),
  )
  invalidateAcademicCache()
  return result
}

export async function removeManualEquivalence(componentId, slotOrder) {
  const result = await apiDelete(
    `/historicos/componentes/${encodeURIComponent(componentId)}/vagas/${encodeURIComponent(slotOrder)}/equivalencia`,
    getAccessToken(),
  )
  invalidateAcademicCache()
  return result
}

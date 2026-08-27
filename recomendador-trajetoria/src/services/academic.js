import { apiDelete, apiGet, apiPatch, apiPut, apiUpload } from './api'
import { getAccessToken, getStoredAuth } from './auth'
import { cachedSessionRequest, invalidateSessionCache } from './sessionCache'

const CATALOG_TTL = 60 * 60 * 1000
const STUDENT_TTL = 10 * 60 * 1000

function academicScope() {
  const auth = getStoredAuth()
  return `${auth?.usuario?.id || auth?.perfil?.id || 'sem-usuario'}:academic:`
}

function cachedAcademicGet(key, path, { ttlMs = STUDENT_TTL, force = false } = {}) {
  return cachedSessionRequest(
    `${academicScope()}${key}`,
    () => apiGet(path, getAccessToken()),
    { ttlMs, force },
  )
}

export function invalidateAcademicCache() {
  invalidateSessionCache(academicScope())
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

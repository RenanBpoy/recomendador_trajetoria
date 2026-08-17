import { apiGet } from './api'
import { getAccessToken } from './auth'

function authenticatedGet(path) {
  return apiGet(path, getAccessToken())
}

export function listCourseCurricula(courseCode) {
  return authenticatedGet(`/cursos/${encodeURIComponent(courseCode)}/ppcs`)
}

export function listCurriculumComponents(curriculumId) {
  return authenticatedGet(`/ppcs/${encodeURIComponent(curriculumId)}/componentes`)
}

export function getSchoolHistory(registration) {
  return authenticatedGet(`/alunos/${encodeURIComponent(registration)}/historico`)
}

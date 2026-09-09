import { apiGet } from './api'
import { getAccessToken, getStoredAuth } from './auth'
import { cachedSessionRequest } from './sessionCache'

function load(path) {
  const user = getStoredAuth()?.usuario?.id || 'sem-usuario'
  return cachedSessionRequest(`${user}:professores:${path}`, () => apiGet(path, getAccessToken()))
}

export function buscarProfessores(nome = '', inicio = 0) {
  return load(`/professores?${new URLSearchParams({ nome, inicio, limite: 30 })}`)
}

export function obterProfessor(id) {
  return load(`/professores/${encodeURIComponent(id)}`)
}

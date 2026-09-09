import { apiGet } from './api'
import { getStoredAuth, getAccessToken } from './auth'
import { cachedSessionRequest } from './sessionCache'

export function carregarConsulta(path) {
  // Não persistir diários identificáveis no cache de sessão do navegador.
  if (path.startsWith('/diarios-classe/')) return apiGet(path, getAccessToken())
  return cachedSessionRequest(`${getStoredAuth()?.usuario?.id}:consulta:${path}`, () => apiGet(path, getAccessToken()))
}

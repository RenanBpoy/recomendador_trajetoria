import { beginLoading } from './loading'

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'request_failed', details = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

async function request(path, {
  method = 'GET',
  body,
  accessToken,
  loadingMessage = 'Salomão está buscando seus dados...',
} = {}) {
  const finishLoading = beginLoading(loadingMessage)
  const headers = {}
  const isFormData = body instanceof FormData
  if (body !== undefined && !isFormData) headers['Content-Type'] = 'application/json'
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`

  try {
    let response
    try {
      response = await fetch(`${API_BASE_URL}${path}`, {
        method,
        headers,
        body: body === undefined ? undefined : (isFormData ? body : JSON.stringify(body)),
      })
    } catch (error) {
      throw new ApiError(
        'Não foi possível conectar à API. Verifique se ela está em execução.',
        { code: 'network_error', details: error },
      )
    }

    let payload = null
    try {
      payload = await response.json()
    } catch {
      // A mensagem genérica abaixo cobre respostas inesperadas sem JSON.
    }

    if (!response.ok) {
      throw new ApiError(
        payload?.error?.message || 'Não foi possível concluir a solicitação.',
        {
          status: response.status,
          code: payload?.error?.code,
          details: payload?.error?.details,
        },
      )
    }

    return payload.data
  } finally {
    finishLoading()
  }
}

export function apiGet(path, accessToken) {
  return request(path, { accessToken })
}

export function apiPost(path, body, accessToken) {
  return request(path, { method: 'POST', body, accessToken })
}

export function apiPut(path, body, accessToken) {
  return request(path, { method: 'PUT', body, accessToken })
}

export function apiPatch(path, body, accessToken) {
  return request(path, { method: 'PATCH', body, accessToken })
}

export function apiDelete(path, accessToken) {
  return request(path, { method: 'DELETE', accessToken })
}

export function apiUpload(path, file, accessToken) {
  const body = new FormData()
  body.append('arquivo', file)
  return request(path, {
    method: 'POST',
    body,
    accessToken,
    loadingMessage: path.includes('/historicos/importacoes')
      ? 'Salomão está lendo seu histórico...'
      : 'Salomão está enviando o arquivo...',
  })
}

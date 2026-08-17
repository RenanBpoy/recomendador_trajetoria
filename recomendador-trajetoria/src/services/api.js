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

async function request(path, { method = 'GET', body, accessToken } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
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
}

export function apiGet(path, accessToken) {
  return request(path, { accessToken })
}

export function apiPost(path, body) {
  return request(path, { method: 'POST', body })
}

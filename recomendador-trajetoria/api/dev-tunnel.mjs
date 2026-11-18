const API_PREFIX = '/api/v1/'
const ROUTE_PARAM = '__salomao_path'
const REQUEST_HEADERS = ['accept', 'authorization', 'content-type']
const RESPONSE_HEADERS = ['content-type', 'retry-after', 'www-authenticate', 'x-request-id']

function error(status, code, message) {
  return Response.json({ error: { code, message } }, {
    status,
    headers: { 'Cache-Control': 'no-store' },
  })
}

export default {
  async fetch(request) {
    const tunnelUrl = process.env.DEV_TUNNEL_URL?.trim()
    const token = process.env.DEV_TUNNEL_TOKEN?.trim()
    const issues = []
    if (!tunnelUrl) issues.push('DEV_TUNNEL_URL ausente')
    if (!token) issues.push('DEV_TUNNEL_TOKEN ausente')
    else if (!/^[A-Za-z0-9._~+/-]+=*$/.test(token)) issues.push('DEV_TUNNEL_TOKEN com formato inválido')

    let origin
    if (tunnelUrl) {
      try {
        origin = new URL(tunnelUrl)
        if (origin.protocol !== 'https:' || !origin.hostname.endsWith('.devtunnels.ms') ||
            origin.username || origin.password || origin.pathname !== '/' || origin.search || origin.hash) {
          issues.push('DEV_TUNNEL_URL inválida')
        }
      } catch {
        issues.push('DEV_TUNNEL_URL inválida')
      }
    }
    if (issues.length) {
      return error(503, 'dev_tunnel_not_configured', `Configuração do túnel: ${issues.join('; ')}.`)
    }

    const incoming = new URL(request.url)
    const paths = incoming.searchParams.getAll(ROUTE_PARAM)
    const path = incoming.pathname.startsWith(API_PREFIX)
      ? incoming.pathname.slice(API_PREFIX.length)
      : paths.length === 1 ? paths[0] : ''
    const segments = path.split('/')
    if (!path || segments.some((segment) => {
      try {
        const decoded = decodeURIComponent(segment)
        return decoded === '.' || decoded === '..' || /[/\\\x00-\x1F\x7F]/.test(decoded)
      } catch {
        return true
      }
    })) {
      return error(400, 'invalid_proxy_path', 'Caminho da API inválido.')
    }

    const target = new URL(origin)
    target.pathname = API_PREFIX + path
    incoming.searchParams.delete(ROUTE_PARAM)
    target.search = incoming.searchParams.toString()

    const headers = new Headers()
    for (const name of REQUEST_HEADERS) {
      if (request.headers.has(name)) headers.set(name, request.headers.get(name))
    }
    headers.set('X-Tunnel-Authorization', `tunnel ${token}`)

    try {
      const { method } = request
      const body = method === 'GET' || method === 'HEAD' ? undefined : await request.arrayBuffer()
      const upstream = await fetch(target, {
        method,
        headers,
        body,
        redirect: 'manual',
        signal: AbortSignal.timeout(120_000),
      })
      const type = upstream.headers.get('content-type') || ''
      if ((upstream.status >= 300 && upstream.status < 400) || /text\/html/i.test(type)) {
        return error(502, 'dev_tunnel_unavailable', 'Não foi possível acessar a API pelo túnel privado. Verifique se ele está ativo e se o token ainda é válido.')
      }

      const resultHeaders = new Headers({ 'Cache-Control': 'no-store' })
      for (const name of RESPONSE_HEADERS) {
        if (upstream.headers.has(name)) resultHeaders.set(name, upstream.headers.get(name))
      }
      return new Response(upstream.body, { status: upstream.status, headers: resultHeaders })
    } catch (cause) {
      if (cause.name === 'TimeoutError') {
        return error(504, 'dev_tunnel_timeout', 'A API demorou demais para responder pelo túnel.')
      }
      return error(502, 'dev_tunnel_unavailable', 'Não foi possível conectar à API pelo túnel privado.')
    }
  },
}

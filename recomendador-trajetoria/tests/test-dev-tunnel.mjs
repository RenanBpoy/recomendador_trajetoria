import assert from 'node:assert/strict'
import { env } from 'node:process'
import test from 'node:test'
import proxy from '../api/dev-tunnel.mjs'

const preview = 'https://preview.vercel.app'
const tunnel = 'https://example-8000.brs.devtunnels.ms'

function configure(t, enabled = true) {
  const originalUrl = env.DEV_TUNNEL_URL
  const originalToken = env.DEV_TUNNEL_TOKEN
  env.DEV_TUNNEL_URL = tunnel
  if (enabled) env.DEV_TUNNEL_TOKEN = 'private-test-token'
  else delete env.DEV_TUNNEL_TOKEN
  t.after(() => {
    if (originalUrl === undefined) delete env.DEV_TUNNEL_URL
    else env.DEV_TUNNEL_URL = originalUrl
    if (originalToken === undefined) delete env.DEV_TUNNEL_TOKEN
    else env.DEV_TUNNEL_TOKEN = originalToken
  })
}

test('forwarding preserves method, body, API auth, query and upstream status', async (t) => {
  configure(t)
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.equal(url.href, `${tunnel}/api/v1/me/plano?filtro=a&filtro=b`)
    assert.equal(options.method, 'PUT')
    assert.equal(options.headers.get('Authorization'), 'Bearer app-session')
    assert.equal(options.headers.get('X-Tunnel-Authorization'), 'tunnel private-test-token')
    assert.equal(options.headers.get('Content-Type'), 'application/json')
    assert.equal(options.headers.get('Cookie'), null)
    assert.equal(options.redirect, 'manual')
    assert.equal(new TextDecoder().decode(options.body), '{"itens":[]}')
    return Response.json({ error: { code: 'test' } }, { status: 409 })
  })
  const result = await proxy.fetch(new Request(
    `${preview}/api/dev-tunnel?__salomao_path=me%2Fplano&filtro=a&filtro=b`,
    {
      method: 'PUT',
      body: '{"itens":[]}',
      headers: {
        Authorization: 'Bearer app-session',
        'X-Tunnel-Authorization': 'untrusted-client-token',
        'Content-Type': 'application/json',
        Cookie: 'preview=internal',
      },
    },
  ))
  assert.equal(result.status, 409)
  assert.equal(result.headers.get('Cache-Control'), 'no-store')
  assert.deepEqual(await result.json(), { error: { code: 'test' } })
})

test('tunnel login redirects are not passed to the browser', async (t) => {
  configure(t)
  t.mock.method(globalThis, 'fetch', async () => Response.redirect('https://login.example.com'))
  const result = await proxy.fetch(new Request(`${preview}/api/v1/status`))
  assert.equal(result.status, 502)
  assert.equal(result.headers.get('Location'), null)
})

test('a malformed path cannot escape the API prefix', async (t) => {
  configure(t)
  const upstream = t.mock.method(globalThis, 'fetch')
  const result = await proxy.fetch(new Request(`${preview}/api/dev-tunnel?__salomao_path=..%2Fstatus`))
  assert.equal(result.status, 400)
  assert.equal(upstream.mock.callCount(), 0)
})

test('without a tunnel token the proxy returns a configuration error', async (t) => {
  configure(t, false)
  const upstream = t.mock.method(globalThis, 'fetch')
  const result = await proxy.fetch(new Request(`${preview}/api/v1/status`))
  assert.equal(result.status, 503)
  assert.equal(upstream.mock.callCount(), 0)
})

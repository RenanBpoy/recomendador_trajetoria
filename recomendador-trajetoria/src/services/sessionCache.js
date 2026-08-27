const CACHE_PREFIX = 'recomendador_trajetoria.session_cache.v1:'
const memoryCache = new Map()
const pendingRequests = new Map()

function storageKey(key) {
  return `${CACHE_PREFIX}${key}`
}

function readStorage(key) {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.sessionStorage.getItem(storageKey(key))
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function writeStorage(key, entry) {
  if (typeof window === 'undefined') return
  try {
    window.sessionStorage.setItem(storageKey(key), JSON.stringify(entry))
  } catch {
    // O cache em memória continua funcionando quando a cota do navegador acaba.
  }
}

function readValidEntry(key) {
  const entry = memoryCache.get(key) || readStorage(key)
  if (!entry) return null
  if (entry.expiresAt <= Date.now()) {
    invalidateSessionCache(key)
    return null
  }
  memoryCache.set(key, entry)
  return entry
}

export function setSessionCache(key, data, ttlMs) {
  const entry = { data, expiresAt: Date.now() + ttlMs }
  memoryCache.set(key, entry)
  writeStorage(key, entry)
  return data
}

export async function cachedSessionRequest(
  key,
  loader,
  { ttlMs = 10 * 60 * 1000, force = false } = {},
) {
  if (!force) {
    const cached = readValidEntry(key)
    if (cached) return cached.data
  }

  if (pendingRequests.has(key)) return pendingRequests.get(key)

  const pending = Promise.resolve()
    .then(loader)
    .then((data) => setSessionCache(key, data, ttlMs))
    .finally(() => pendingRequests.delete(key))

  pendingRequests.set(key, pending)
  return pending
}

export function invalidateSessionCache(keyPrefix) {
  for (const key of [...memoryCache.keys()]) {
    if (key.startsWith(keyPrefix)) memoryCache.delete(key)
  }
  if (typeof window === 'undefined') return
  try {
    for (let index = window.sessionStorage.length - 1; index >= 0; index -= 1) {
      const key = window.sessionStorage.key(index)
      if (key?.startsWith(storageKey(keyPrefix))) window.sessionStorage.removeItem(key)
    }
  } catch {
    // Sem persistência, o cache em memória ainda é removido acima.
  }
}

export function clearSessionCache() {
  memoryCache.clear()
  pendingRequests.clear()
  if (typeof window === 'undefined') return
  try {
    for (let index = window.sessionStorage.length - 1; index >= 0; index -= 1) {
      const key = window.sessionStorage.key(index)
      if (key?.startsWith(CACHE_PREFIX)) window.sessionStorage.removeItem(key)
    }
  } catch {
    // Nada a fazer quando sessionStorage não está disponível.
  }
}

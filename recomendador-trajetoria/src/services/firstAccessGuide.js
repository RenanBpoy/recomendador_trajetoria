const GUIDE_STORAGE_PREFIX = 'recomendador_trajetoria.first_access_guide.v1:'
const PROFILE_GUIDE_STORAGE_PREFIX = 'recomendador_trajetoria.profile_guide.v1:'

export const FIRST_ACCESS_GUIDE_CHANGED_EVENT = 'recomendador-trajetoria:first-access-guide-changed'

function storageKey(userId) {
  return `${GUIDE_STORAGE_PREFIX}${userId}`
}

function profileStorageKey(userId) {
  return `${PROFILE_GUIDE_STORAGE_PREFIX}${userId}`
}

function notifyGuideChanged(userId, action) {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(FIRST_ACCESS_GUIDE_CHANGED_EVENT, {
    detail: { userId, action },
  }))
}

export function shouldShowFirstAccessGuide(userId) {
  if (!userId || typeof window === 'undefined') return false
  try {
    return window.localStorage.getItem(storageKey(userId)) === null
  } catch {
    return true
  }
}

export function completeFirstAccessGuide(userId) {
  if (!userId || typeof window === 'undefined') return
  try {
    window.localStorage.setItem(storageKey(userId), JSON.stringify({
      completedAt: new Date().toISOString(),
    }))
  } catch {
    // O guia continua fechando na sessão atual se o armazenamento estiver indisponível.
  }
  notifyGuideChanged(userId, 'complete')
}

export function restartFirstAccessGuide(userId) {
  if (!userId || typeof window === 'undefined') return
  try {
    window.localStorage.removeItem(storageKey(userId))
  } catch {
    // O evento abaixo ainda permite reiniciar o guia na sessão atual.
  }
  notifyGuideChanged(userId, 'restart')
}

export function shouldShowProfileGuide(userId) {
  if (!userId || typeof window === 'undefined') return false
  try {
    return window.localStorage.getItem(profileStorageKey(userId)) === null
  } catch {
    return true
  }
}

export function completeProfileGuide(userId) {
  if (!userId || typeof window === 'undefined') return
  try {
    window.localStorage.setItem(profileStorageKey(userId), JSON.stringify({
      completedAt: new Date().toISOString(),
    }))
  } catch {
    // O guia continua fechando na sessão atual se o armazenamento estiver indisponível.
  }
}

export function restartProfileGuide(userId) {
  if (!userId || typeof window === 'undefined') return
  try {
    window.localStorage.removeItem(profileStorageKey(userId))
  } catch {
    // A próxima visita ainda poderá iniciar o guia quando o armazenamento voltar a funcionar.
  }
}

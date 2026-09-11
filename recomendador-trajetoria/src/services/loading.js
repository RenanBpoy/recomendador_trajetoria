const listeners = new Set()
const requests = new Map()

export const LOADING_QUOTES = [
  'Uma vida sem reflexão… bem, você sabe o resto.',
  'Só sei que nada sei. Acho que era essa.',
  'A resposta está no caminho… ou perto dele.',
  'Penso, logo existo. Pelo menos foi o que concluí da última vez.',
  'A dúvida é o princípio da sabedoria. Então estamos indo bem.',
  'Grandes ideias costumam começar com uma pergunta. Ou com um silêncio longo.',
  'Há mais de um caminho para chegar a uma boa resposta.',
]

let nextRequestId = 0
let sessionId = 0
let completionTimer = null
let lastMessage = 'Salomão está buscando seus dados...'
let quoteIndex = 0
let snapshot = {
  active: false,
  visible: false,
  sessionId,
  message: lastMessage,
  quote: LOADING_QUOTES[quoteIndex],
}

function notify() {
  listeners.forEach((listener) => listener())
}

export function beginLoading(message) {
  if (!requests.size) {
    sessionId += 1
    if (completionTimer) window.clearTimeout(completionTimer)
    const offset = 1 + Math.floor(Math.random() * (LOADING_QUOTES.length - 1))
    quoteIndex = (quoteIndex + offset) % LOADING_QUOTES.length
  }

  const requestId = ++nextRequestId
  lastMessage = message || lastMessage
  requests.set(requestId, lastMessage)
  snapshot = {
    active: true,
    visible: true,
    sessionId,
    message: lastMessage,
    quote: LOADING_QUOTES[quoteIndex],
  }
  notify()

  let finished = false
  return () => {
    if (finished) return
    finished = true
    requests.delete(requestId)

    if (requests.size) {
      lastMessage = [...requests.values()].at(-1)
      snapshot = { ...snapshot, message: lastMessage }
      notify()
      return
    }

    snapshot = { ...snapshot, active: false, visible: true }
    notify()
    completionTimer = window.setTimeout(() => {
      snapshot = { ...snapshot, visible: false }
      completionTimer = null
      notify()
    }, 280)
  }
}

export function subscribeToLoading(listener) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function getLoadingSnapshot() {
  return snapshot
}

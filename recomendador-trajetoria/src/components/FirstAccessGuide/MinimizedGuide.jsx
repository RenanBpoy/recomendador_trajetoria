import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import readingMascot from '../../assets/img/reading.png'
import sleepingMascot from '../../assets/img/salomao-sleeping.png'

const size = 120
const sleepDelay = 60_000
function viewportBounds() {
  const width = Math.min(window.innerWidth, 430)
  const inset = Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--app-frame-inset')) || 0
  const left = (window.innerWidth - width) / 2
  return document.getElementById('app-viewport')?.getBoundingClientRect()
    || { left, top: inset, right: left + width, bottom: window.innerHeight - inset }
}
function constrain(x, y) {
  const bounds = viewportBounds()
  return {
    x: Math.max(bounds.left + 8, Math.min(x, bounds.right - size - 8)),
    y: Math.max(bounds.top + 8, Math.min(y, bounds.bottom - size - 8)),
  }
}

export default function MinimizedGuide({ onResume, checking, error, label = 'Retomar guia. Segure e arraste para mover.', buttonRef }) {
  const [position, setPosition] = useState(() => {
    const bounds = viewportBounds()
    return constrain(bounds.right - size - 16, bounds.bottom - size - 94)
  })
  const [sleeping, setSleeping] = useState(false)
  const drag = useRef(null)
  const suppressClick = useRef(false)
  const sleepTimer = useRef(null)

  function restartSleepTimer() {
    window.clearTimeout(sleepTimer.current)
    setSleeping(false)
    sleepTimer.current = window.setTimeout(() => setSleeping(true), sleepDelay)
  }

  useEffect(() => {
    const resize = () => setPosition((current) => constrain(current.x, current.y))
    window.addEventListener('resize', resize)
    window.visualViewport?.addEventListener('resize', resize)
    return () => {
      window.removeEventListener('resize', resize)
      window.visualViewport?.removeEventListener('resize', resize)
    }
  }, [])

  useEffect(() => {
    sleepTimer.current = window.setTimeout(() => setSleeping(true), sleepDelay)
    return () => window.clearTimeout(sleepTimer.current)
  }, [])

  return createPortal(
    <>
      <button
        ref={buttonRef}
        className="minimized-guide"
        style={{ left: position.x, top: position.y }}
        type="button"
        aria-label={checking ? 'Conferindo progresso do guia' : label}
        aria-busy={checking}
        onPointerDown={(event) => {
          if (event.button !== 0) return
          suppressClick.current = false
          drag.current = { x: event.clientX, y: event.clientY, origin: position, id: event.pointerId }
          event.currentTarget.setPointerCapture(event.pointerId)
        }}
        onPointerMove={(event) => {
          const start = drag.current
          if (!start || start.id !== event.pointerId) return
          const dx = event.clientX - start.x
          const dy = event.clientY - start.y
          if (Math.hypot(dx, dy) > 6) suppressClick.current = true
          if (suppressClick.current) setPosition(constrain(start.origin.x + dx, start.origin.y + dy))
        }}
        onPointerUp={() => { drag.current = null }}
        onPointerCancel={() => { drag.current = null; suppressClick.current = true }}
        onLostPointerCapture={() => { drag.current = null }}
        onClick={(event) => {
          if (suppressClick.current) { suppressClick.current = false; return }
          restartSleepTimer()
          if (!checking) onResume?.(event.currentTarget)
        }}
      >
        <img src={sleeping ? sleepingMascot : readingMascot} alt="" draggable={false} />
      </button>
      {error && <p className="minimized-guide__error" role="alert">{error}</p>}
    </>, document.body,
  )
}

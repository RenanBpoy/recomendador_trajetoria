import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import readingMascot from '../../assets/img/reading.png'

const size = 120
function constrain(x, y) {
  return { x: Math.max(8, Math.min(x, window.innerWidth - size - 8)), y: Math.max(8, Math.min(y, window.innerHeight - size - 8)) }
}

export default function MinimizedGuide({ onResume, checking, error, label = 'Retomar guia. Segure e arraste para mover.', buttonRef }) {
  const [position, setPosition] = useState(() => constrain(window.innerWidth - size - 16, window.innerHeight - size - 94))
  const drag = useRef(null)
  const suppressClick = useRef(false)

  useEffect(() => {
    const resize = () => setPosition((current) => constrain(current.x, current.y))
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
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
          if (!checking) onResume?.(event.currentTarget)
        }}
      >
        <img src={readingMascot} alt="" draggable={false} />
      </button>
      {error && <p className="minimized-guide__error" role="alert">{error}</p>}
    </>, document.body,
  )
}

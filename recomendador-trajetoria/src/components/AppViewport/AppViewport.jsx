import { useLayoutEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

export default function AppViewport({ children }) {
  const { pathname } = useLocation()
  const scrollRef = useRef(null)

  useLayoutEffect(() => {
    scrollRef.current?.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [pathname])

  return (
    <div id="app-viewport" className="app-viewport">
      <div ref={scrollRef} className="app-viewport__scroll">{children}</div>
    </div>
  )
}

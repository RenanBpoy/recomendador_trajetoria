import { useEffect, useState, useSyncExternalStore } from 'react'
import readingMascot from '../../assets/img/reading.png'
import {
  getLoadingSnapshot,
  subscribeToLoading,
} from '../../services/loading'
import './LoadingScreen.css'

const INITIAL_PROGRESS = 8
const WAITING_LIMIT = 92

function LoadingProgress({ complete }) {
  const [progress, setProgress] = useState(INITIAL_PROGRESS)

  useEffect(() => {
    if (complete) return undefined

    const interval = window.setInterval(() => {
      setProgress((current) => {
        if (current >= WAITING_LIMIT) return current
        const remaining = WAITING_LIMIT - current
        return Math.min(WAITING_LIMIT, current + Math.max(1, Math.ceil(remaining * 0.09)))
      })
    }, 180)

    return () => window.clearInterval(interval)
  }, [complete])

  const currentProgress = complete ? 100 : progress
  const roundedProgress = Math.round(currentProgress)

  return (
    <div className="loading-screen__progress">
      <div
        className="loading-screen__track"
        role="progressbar"
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={roundedProgress}
      >
        <span style={{ width: `${roundedProgress}%` }} />
      </div>
      <p>Estou cuidando disso!</p>
    </div>
  )
}

function LoadingScreen() {
  const loading = useSyncExternalStore(
    subscribeToLoading,
    getLoadingSnapshot,
    getLoadingSnapshot,
  )
  if (!loading.visible) return null

  return (
    <div className="loading-screen" role="status" aria-live="polite" aria-label="Estou cuidando disso">
      <div className="loading-screen__content">
        <div className="loading-screen__intro">
          <span>TCC</span>
          <h1>Salomão está pensando...</h1>
          <p>Boas escolhas levam um pouquinho de tempo.</p>
        </div>

        <img
          className="loading-screen__mascot"
          src={readingMascot}
          alt="Salomão lendo um livro enquanto os dados são carregados"
        />

        <LoadingProgress key={loading.sessionId} complete={!loading.active} />

        <blockquote className="loading-screen__quote">
          <p>“{loading.quote}”</p>
          <cite>— Salomão</cite>
        </blockquote>
      </div>
    </div>
  )
}

export default LoadingScreen

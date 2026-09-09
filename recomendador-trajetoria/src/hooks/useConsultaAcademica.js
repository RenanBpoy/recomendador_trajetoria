import { useEffect, useState } from 'react'
import { carregarConsulta } from '../services/consultas'

export function useConsultaAcademica(path) {
  const [state, setState] = useState({ path: '', data: null, error: '' })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let active = true
    carregarConsulta(path).then((data) => { if (active) setState({ path, data, error: '' }) })
      .catch((err) => { if (active) setState({ path, data: null, error: err.message }) })
    return () => { active = false }
  }, [path, attempt])
  return {
    data: state.path === path ? state.data : null,
    error: state.path === path ? state.error : '',
    retry: () => { setState({ path: '', data: null, error: '' }); setAttempt((n) => n + 1) },
  }
}

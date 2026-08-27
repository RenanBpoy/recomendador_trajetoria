import { useEffect, useState } from 'react'
import { useStoredAuth } from './useStoredAuth'
import {
  getSchoolHistory,
  getCurriculum,
  listCurriculumComponents,
  listManualEquivalences,
} from '../services/academic'
import { buildCurriculumProgress } from '../utils/curriculum'

const emptySummary = {
  approved: 0,
  pending: 0,
  failed: 0,
  percentage: 0,
  remainingHours: 0,
}

function summarizeProgress(progress, curriculum) {
  const approved = progress.filter((item) => item.estado_academico.key === 'approved')
  const failed = progress.filter((item) => item.estado_academico.key === 'failed')
  const pending = progress.length - approved.length - failed.length
  const approvedHours = approved.reduce(
    (total, item) => total + Number(item.carga_horaria || 0),
    0,
  )
  const componentsHours = progress.reduce(
    (total, item) => total + Number(item.carga_horaria || 0),
    0,
  )
  const totalHours = Number(curriculum?.carga_horaria_total || componentsHours)

  return {
    approved: approved.length,
    pending,
    failed: failed.length,
    percentage: totalHours > 0 ? Math.min(100, Math.round((approvedHours / totalHours) * 100)) : 0,
    remainingHours: Math.max(0, totalHours - approvedHours),
  }
}

export function useAcademicProgress() {
  const profile = useStoredAuth()?.perfil
  const [curriculum, setCurriculum] = useState(null)
  const [summary, setSummary] = useState(emptySummary)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadProgress() {
      if (!profile?.curso_codigo || !profile?.matricula) {
        if (active) {
          setError('Não foi possível identificar o contexto acadêmico do usuário.')
          setLoading(false)
        }
        return
      }
      if (!profile?.ppc_id) {
        if (active) {
          setError('Escolha seu PPC no perfil para calcular o progresso acadêmico.')
          setLoading(false)
        }
        return
      }

      try {
        const [selectedCurriculum, history, components, manualMappings] = await Promise.all([
          getCurriculum(profile.ppc_id),
          getSchoolHistory(profile.matricula),
          listCurriculumComponents(profile.ppc_id),
          listManualEquivalences(),
        ])
        const progress = buildCurriculumProgress(components, history, manualMappings)

        if (active) {
          setCurriculum(selectedCurriculum)
          setSummary(summarizeProgress(progress, selectedCurriculum))
        }
      } catch (requestError) {
        if (active) {
          setError(requestError.message || 'Não foi possível carregar o progresso acadêmico.')
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    loadProgress()
    return () => { active = false }
  }, [profile?.curso_codigo, profile?.matricula, profile?.ppc_id])

  return { profile, curriculum, summary, loading, error }
}

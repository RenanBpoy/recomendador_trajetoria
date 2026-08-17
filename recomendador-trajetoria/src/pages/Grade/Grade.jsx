import { WandSparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import CurriculumPanel from '../../components/CurriculumPanel/CurriculumPanel'
import { getStoredAuth } from '../../services/auth'
import {
  getSchoolHistory,
  listCourseCurricula,
  listCurriculumComponents,
} from '../../services/academic'
import './Grade.css'

function Grade() {
  const profile = getStoredAuth()?.perfil
  const [curricula, setCurricula] = useState([])
  const [selectedCurriculumId, setSelectedCurriculumId] = useState('')
  const [components, setComponents] = useState([])
  const [history, setHistory] = useState([])
  const [contextLoading, setContextLoading] = useState(true)
  const [componentsLoading, setComponentsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadAcademicContext() {
      if (!profile?.curso_codigo || !profile?.matricula) {
        if (active) {
          setError('Entre novamente para carregar seu curso e sua matrícula.')
          setContextLoading(false)
        }
        return
      }

      try {
        const [courseCurricula, schoolHistory] = await Promise.all([
          listCourseCurricula(profile.curso_codigo),
          getSchoolHistory(profile.matricula),
        ])
        if (!active) return

        setCurricula(courseCurricula)
        setHistory(schoolHistory)
        const defaultCurriculum = courseCurricula.find((item) => item.curriculo_corrente)
          || courseCurricula[0]
        if (!defaultCurriculum) {
          setError('Nenhum PPC foi encontrado para o curso do usuário.')
          return
        }
        setSelectedCurriculumId(String(defaultCurriculum.id))
      } catch (requestError) {
        if (active) setError(requestError.message || 'Não foi possível carregar os dados acadêmicos.')
      } finally {
        if (active) setContextLoading(false)
      }
    }

    loadAcademicContext()
    return () => { active = false }
  }, [profile?.curso_codigo, profile?.matricula])

  useEffect(() => {
    let active = true

    async function loadComponents() {
      if (!selectedCurriculumId) return
      setComponentsLoading(true)
      setError('')
      try {
        const curriculumComponents = await listCurriculumComponents(selectedCurriculumId)
        if (active) setComponents(curriculumComponents)
      } catch (requestError) {
        if (active) setError(requestError.message || 'Não foi possível carregar a sequência do PPC.')
      } finally {
        if (active) setComponentsLoading(false)
      }
    }

    loadComponents()
    return () => { active = false }
  }, [selectedCurriculumId])

  return (
    <main className="mobile-page grade-page">
      <AppHeader title="Grade curricular" icon={WandSparkles} ariaLabel="Gerar grade recomendada" />
      <div className="grade-page__content">
        <section className="academic-context" aria-label="Contexto acadêmico">
          <div>
            <span>Curso do estudante</span>
            <strong>{profile?.curso_codigo || '—'}</strong>
          </div>
          <small>Matrícula {profile?.matricula || 'não identificada'}</small>
        </section>

        <div className="ppc-selector">
          <span>Currículo utilizado</span>
          <div className="semester-tabs ppc-tabs" aria-label="Selecionar PPC">
            {curricula.map((curriculum) => {
              const curriculumId = String(curriculum.id)
              const isSelected = curriculumId === selectedCurriculumId

              return (
                <button
                  key={curriculum.id}
                  type="button"
                  className={isSelected ? 'is-active' : ''}
                  aria-pressed={isSelected}
                  disabled={contextLoading}
                  onClick={() => setSelectedCurriculumId(curriculumId)}
                >
                  {curriculum.ano_versao}
                </button>
              )
            })}
            {curricula.length === 0 && (
              <button type="button" disabled>{contextLoading ? '...' : '—'}</button>
            )}
          </div>
        </div>

        {error && <p className="form-feedback is-error" role="alert">{error}</p>}
        <CurriculumPanel
          key={selectedCurriculumId || 'empty'}
          components={components}
          history={history}
          loading={contextLoading || componentsLoading}
        />
        <button className="primary-button grade-page__button" type="button">Continuar</button>
      </div>
      <BottomNav active="grade" lastItem="plano" />
    </main>
  )
}

export default Grade

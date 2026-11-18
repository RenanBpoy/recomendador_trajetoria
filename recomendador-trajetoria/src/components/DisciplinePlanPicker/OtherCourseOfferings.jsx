import { ChevronDown, GraduationCap, LoaderCircle } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { listInstitutionalPlanOfferings, listOtherPlanCourses } from '../../services/academic'
import DisciplinePlanPicker from './DisciplinePlanPicker'

function courseLoadError(error, fallback) {
  if (error.status === 429) {
    return 'A UFSM limitou temporariamente as consultas. Tente novamente mais tarde.'
  }
  return error.message || fallback
}

function CourseDropdown({ course, slot, planItems, selectedOfferingId, onSelect }) {
  const [opened, setOpened] = useState(false)
  const [offerings, setOfferings] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inFlight = useRef(false)

  async function load() {
    if (offerings !== null || inFlight.current) return
    inFlight.current = true
    setError('')
    setLoading(true)
    try {
      const { itens } = await listInstitutionalPlanOfferings(slot, course.codigo)
      setOfferings(itens)
    } catch (requestError) {
      setError(courseLoadError(requestError, 'Não foi possível buscar as ofertas desse curso.'))
    } finally {
      inFlight.current = false
      setLoading(false)
    }
  }

  function toggle(event) {
    const isOpen = event.currentTarget.open
    setOpened(isOpen)
    if (isOpen) load()
  }

  return (
    <details className="discipline-plan-picker__course" onToggle={toggle}>
      <summary>
        <span className="discipline-plan-picker__course-icon"><GraduationCap size={17} aria-hidden="true" /></span>
        <span className="discipline-plan-picker__course-label">
          <strong>{course.nome}</strong>
          <small>{offerings === null ? 'Ver turmas neste horário'
            : offerings.length === 0 ? 'Sem turmas neste horário'
            : offerings.length === 1 ? '1 turma neste horário' : `${offerings.length} turmas neste horário`}</small>
        </span>
        <ChevronDown className="discipline-plan-picker__chevron" size={16} aria-hidden="true" />
      </summary>
      {opened && (
        <div className="discipline-plan-picker__course-body">
          <DisciplinePlanPicker
            compact
            showHeading={false}
            disciplines={offerings || []}
            selectedOfferingId={selectedOfferingId}
            loading={loading || (offerings === null && !error)}
            error={error}
            planItems={planItems}
            editingItem={slot}
            onSelect={onSelect}
          />
        </div>
      )}
    </details>
  )
}

export default function OtherCourseOfferings({ slot, planItems, selectedOfferingId, onSelect }) {
  const [courses, setCourses] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    listOtherPlanCourses()
      .then(({ itens }) => { if (active) setCourses(itens) })
      .catch((requestError) => {
        if (active) setError(courseLoadError(requestError, 'Não foi possível listar outros cursos.'))
      })
    return () => { active = false }
  }, [])

  return (
    <section className="discipline-plan-picker__other-courses" aria-label="Ofertas de outros cursos">
      <strong>Outros cursos</strong>
      <p>Abra um curso para consultar as turmas no horário selecionado.</p>
      {courses?.map((course) => (
        <CourseDropdown key={course.codigo} {...{ course, slot, planItems, selectedOfferingId, onSelect }} />
      ))}
      {error && <p role="alert">{error}</p>}
      {!error && courses === null && <p className="discipline-plan-picker__scan-status" role="status">
        <LoaderCircle size={15} aria-hidden="true" />Carregando lista de cursos…
      </p>}
      {courses?.length === 0 && <p>Nenhum outro curso encontrado.</p>}
    </section>
  )
}

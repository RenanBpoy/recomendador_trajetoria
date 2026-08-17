import { Check, Clock3, Pause, Search, X } from 'lucide-react'
import { useMemo, useState } from 'react'
import { buildCurriculumProgress } from '../../utils/curriculum'
import './CurriculumPanel.css'

const statusVisuals = {
  approved: { tone: 'green', icon: Check },
  pending: { tone: 'blue', icon: Clock3 },
  failed: { tone: 'pink', icon: X },
  interrupted: { tone: 'yellow', icon: Pause },
}

const summaryItems = [
  { key: 'approved', label: 'Concluídas', tone: 'green', icon: Check },
  { key: 'pending', label: 'Pendentes', tone: 'blue', icon: Clock3 },
  { key: 'failed', label: 'Reprovadas', tone: 'pink', icon: X },
  { key: 'interrupted', label: 'Não concluídas', tone: 'yellow', icon: Pause },
]

function CurriculumPanel({ components, history, loading }) {
  const [activeSemester, setActiveSemester] = useState(1)
  const [search, setSearch] = useState('')

  const progress = useMemo(
    () => buildCurriculumProgress(components, history),
    [components, history],
  )
  const semesters = useMemo(
    () => [...new Set(progress.map((item) => item.semestre_recomendado))].sort((a, b) => a - b),
    [progress],
  )
  const normalizedSearch = search.trim().toLocaleLowerCase('pt-BR')
  const visibleComponents = progress.filter((component) => {
    if (component.semestre_recomendado !== activeSemester) return false
    if (!normalizedSearch) return true
    const searchable = [
      component.disciplina_codigo,
      component.disciplina_nome,
      component.nome_no_ppc,
    ].filter(Boolean).join(' ').toLocaleLowerCase('pt-BR')
    return searchable.includes(normalizedSearch)
  })
  const stats = summaryItems.map((item) => ({
    ...item,
    count: progress.filter((component) => component.estado_academico.key === item.key).length,
  }))

  if (loading) {
    return <div className="curriculum-panel curriculum-panel__state" role="status">Carregando grade e histórico...</div>
  }

  if (progress.length === 0) {
    return <div className="curriculum-panel curriculum-panel__state">Nenhum componente encontrado para este PPC.</div>
  }

  return (
    <div className="curriculum-panel">
      <div className="semester-tabs" aria-label="Semestres">
        {semesters.map((semester) => (
          <button
            key={semester}
            type="button"
            className={semester === activeSemester ? 'is-active' : ''}
            aria-pressed={semester === activeSemester}
            onClick={() => setActiveSemester(semester)}
          >
            {semester}º
          </button>
        ))}
      </div>

      <label className="course-search">
        <Search size={14} />
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Buscar disciplina neste semestre"
          aria-label="Buscar disciplina"
        />
      </label>

      <div className="course-stats">
        {stats.map(({ key, count, label, tone, icon: Icon }) => (
          <article key={key} className={`course-stat course-stat--${tone}`}>
            <div><Icon size={14} strokeWidth={3} /><strong>{count}</strong></div>
            <span>{label}</span>
          </article>
        ))}
      </div>

      <section className="course-list">
        <header>
          <strong>▤ &nbsp;{activeSemester}º semestre</strong>
          <span>{visibleComponents.length} componentes</span>
        </header>
        <div className="course-list__items">
          {visibleComponents.map((component) => {
            const visual = statusVisuals[component.estado_academico.key]
            const Icon = visual.icon
            const latest = component.tentativa_mais_recente
            const componentName = component.disciplina_nome || component.nome_no_ppc
            const details = [
              component.disciplina_codigo,
              `${component.carga_horaria} h`,
              latest ? `última tentativa ${latest.ano}/${latest.semestre}` : null,
            ].filter(Boolean).join(' • ')

            return (
              <article key={component.id} className="course-row">
                <span className={`course-row__icon course-row__icon--${visual.tone}`}><Icon size={18} strokeWidth={3} /></span>
                <span className="course-row__copy"><strong>{componentName}</strong><small>{details}</small></span>
                <span className={`course-row__status course-row__status--${visual.tone}`}>{component.estado_academico.label}</span>
                <span className="course-row__arrow">›</span>
              </article>
            )
          })}
          {visibleComponents.length === 0 && <p className="course-list__empty">Nenhuma disciplina encontrada.</p>}
        </div>
      </section>
    </div>
  )
}

export default CurriculumPanel

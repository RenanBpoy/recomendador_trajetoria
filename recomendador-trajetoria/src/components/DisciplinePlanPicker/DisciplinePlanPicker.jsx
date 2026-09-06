import { AlertTriangle, Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import { classifyOfferingsByPlan } from '../../utils/disciplineAvailability'
import { weeklyActivityLabel } from '../../utils/weeklyPlan'
import './DisciplinePlanPicker.css'

function normalize(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
}

function ConflictMeeting({ schedule, activity }) {
  const dayNames = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']
  const day = schedule.dia_nome || dayNames[activity.dia_semana] || 'Dia não informado'
  const activityName = activity.titulo || weeklyActivityLabel(activity.tipo_atividade)
  return (
    <span className="discipline-plan-picker__conflict">
      <span className="discipline-plan-picker__conflict-day">
        <AlertTriangle size={12} aria-hidden="true" />
        Conflito: {day}
      </span>
      <span className="discipline-plan-picker__meeting">
        <span className="discipline-plan-picker__blocking-activity">{activityName}</span>
        <span className="discipline-plan-picker__time">
          {String(activity.hora_inicio).slice(0, 5)} às {String(activity.hora_fim).slice(0, 5)}
        </span>
      </span>
    </span>
  )
}

function DisciplinePlanPicker({
  disciplines,
  selectedOfferingId,
  loading,
  error,
  planItems = [],
  editingItem = null,
  showHeading = true,
  onSelect,
}) {
  const [query, setQuery] = useState('')
  const filtered = useMemo(() => {
    const search = normalize(query.trim())
    if (!search) return disciplines
    return disciplines.filter((offering) => (
      normalize(`${offering.disciplina_codigo} ${offering.disciplina_nome} ${offering.codigo_turma}`).includes(search)
    ))
  }, [disciplines, query])
  const groups = useMemo(
    () => classifyOfferingsByPlan(filtered, planItems, editingItem),
    [editingItem, filtered, planItems],
  )

  function renderOption({ offering, conflicts }, hasConflict = false) {
    const selected = offering.id === selectedOfferingId
    const visibleConflicts = conflicts.slice(0, 2)
    const remainingConflicts = conflicts.length - visibleConflicts.length
    return (
      <button
        key={offering.id}
        type="button"
        role="option"
        aria-selected={selected}
        className={`discipline-plan-picker__option${selected ? ' is-selected' : ''}${hasConflict ? ' has-conflict' : ''}`}
        onClick={() => onSelect(offering)}
      >
        <span className="discipline-plan-picker__option-heading">
          <strong>{offering.disciplina_nome}</strong>
          <span className="discipline-plan-picker__code">{offering.disciplina_codigo}</span>
        </span>
        <span className="discipline-plan-picker__description">
          <span className="discipline-plan-picker__meetings">
            {offering.horarios.map((schedule, index) => (
              <span className="discipline-plan-picker__meeting" key={schedule.id ?? index}>
                <span>{schedule.dia_nome}</span>
                <span className="discipline-plan-picker__time">
                  {String(schedule.hora_inicio).slice(0, 5)} às {String(schedule.hora_fim).slice(0, 5)}
                </span>
              </span>
            ))}
          </span>
          {hasConflict && (
            <span className="discipline-plan-picker__conflict-detail">
              {visibleConflicts.map((conflict, index) => <ConflictMeeting key={index} {...conflict} />)}
              {remainingConflicts > 0 && <span>+{remainingConflicts} conflito(s)</span>}
            </span>
          )}
        </span>
      </button>
    )
  }

  return (
    <section className="discipline-plan-picker" aria-label="Escolher disciplina">
      {showHeading && <div className="discipline-plan-picker__heading">
        <span id="discipline-plan-picker-title">Disciplina</span>
        {!loading && !error && <small>{disciplines.length} {disciplines.length === 1 ? 'opção' : 'opções'}</small>}
      </div>}

      <label className="discipline-plan-picker__search">
        <Search size={17} aria-hidden="true" />
        <input
          type="search"
          value={query}
          placeholder="Buscar por nome ou código"
          aria-label="Buscar disciplina por nome ou código"
          onChange={(event) => setQuery(event.target.value)}
        />
      </label>

      <div className="discipline-plan-picker__options" role="listbox" aria-label="Disciplinas ainda não aprovadas">
        {loading && <p>Carregando disciplinas...</p>}
        {!loading && error && <p className="is-error">{error}</p>}
        {!loading && !error && !filtered.length && <p>Nenhuma disciplina encontrada.</p>}
        {!loading && !error && filtered.length > 0 && (
          <>
            <section className="discipline-plan-picker__group" aria-labelledby="available-disciplines-title">
              <div className="discipline-plan-picker__group-heading">
                <strong id="available-disciplines-title"><i className="discipline-plan-picker__dot" aria-hidden="true" />Disponíveis</strong>
                <span>{groups.available.length}</span>
              </div>
              {groups.available.length
                ? groups.available.map((entry) => renderOption(entry))
                : <p>Nenhuma turma possui compatibilidade de horário completa.</p>}
            </section>

            {groups.conflicting.length > 0 && (
              <section className="discipline-plan-picker__group discipline-plan-picker__group--conflict" aria-labelledby="conflicting-disciplines-title">
                <div className="discipline-plan-picker__group-heading">
                  <strong id="conflicting-disciplines-title"><AlertTriangle size={11} />Conflito com outra atividade</strong>
                  <span>{groups.conflicting.length}</span>
                </div>
                {groups.conflicting.map((entry) => renderOption(entry, true))}
              </section>
            )}
          </>
        )}
      </div>

      <p className="discipline-plan-picker__hint">
        A busca parte do intervalo selecionado e confere todos os encontros da turma. Resolva os conflitos indicados antes de adicionar a disciplina.
      </p>
    </section>
  )
}

export default DisciplinePlanPicker

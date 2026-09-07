import { weeklyActivityLabel } from '../../utils/weeklyPlan'
import './ScheduleGrid.css'

const days = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
const hours = [8.5, 10.5, 12.5, 14.5, 16.5, 18.5, 20.5]
const activityColors = {
  DISCIPLINA: 'mint',
  ESTAGIO: 'purple',
  OUTRO: 'pink',
}

function hourValue(value) {
  const [hour, minute] = String(value).split(':').map(Number)
  return hour + minute / 60
}

function eventName(entry) {
  return entry.nome_exibicao || entry.titulo || weeklyActivityLabel(entry.tipo_atividade)
}

function eventLabel(entry) {
  const disciplineCode = entry.codigo || entry.disciplina_codigo
  if (entry.tipo_atividade === 'DISCIPLINA' && disciplineCode) return disciplineCode
  return entry.rotulo || eventName(entry).trim().charAt(0).toUpperCase()
}

function ScheduleGrid({ entries = [], onSelectSlot, onSelectEntry, readOnly = false, footerText, endHour = 20 }) {
  const visibleHours = hours.filter((hour) => hour <= endHour + 0.5)
  const gridStart = hours[0]
  const gridEnd = visibleHours[visibleHours.length - 1] + 2
  const visibleEntries = entries.filter((entry) => hourValue(entry.hora_inicio) < gridEnd && hourValue(entry.hora_fim) > gridStart)

  return (
    <section className={`schedule-grid${readOnly ? ' is-readonly' : ''}`} aria-label="Grade semanal">
      <div className="weekly-calendar__grid" style={{ '--schedule-row-count': visibleHours.length }}>
        {days.map((day, index) => (
          <span key={day} className="weekly-calendar__day" style={{ gridColumn: index + 2, gridRow: 1 }}>
            {day}
          </span>
        ))}

        {visibleHours.map((hour, index) => (
          <span key={hour} className="weekly-calendar__hour" style={{ gridColumn: 1, gridRow: index + 2 }}>
            {Math.floor(hour)}h30
          </span>
        ))}

        {days.flatMap((_, dayIndex) => visibleHours.map((hour, rowIndex) => (
          <button
            key={`${dayIndex + 1}-${hour}`}
            className="weekly-calendar__slot"
            type="button"
            style={{ gridColumn: dayIndex + 2, gridRow: rowIndex + 2 }}
            aria-label={readOnly ? undefined : `Adicionar atividade na ${days[dayIndex]} às ${Math.floor(hour)}:30`}
            onClick={() => !readOnly && onSelectSlot?.(dayIndex + 1, hour)}
            disabled={readOnly}
          >
            {!readOnly && <span>+</span>}
          </button>
        )))}

        {visibleEntries.map((entry) => {
          const start = Math.max(gridStart, hourValue(entry.hora_inicio))
          const end = Math.min(gridEnd, hourValue(entry.hora_fim))
          const rowOffset = (start - gridStart) / 2
          const row = Math.floor(rowOffset) + 2
          const span = Math.max(1, Math.ceil((end - gridStart) / 2) - Math.floor(rowOffset))
          const topInset = (rowOffset % 1) / span * 100
          const bottomInset = (Math.floor(rowOffset) + span - (end - gridStart) / 2) / span * 100
          const color = entry.cor || activityColors[entry.tipo_atividade] || 'blue'
          const name = eventName(entry)
          const hasDisciplineCode = entry.tipo_atividade === 'DISCIPLINA'
            && Boolean(entry.codigo || entry.disciplina_codigo)

          return (
            <button
              key={entry._key}
              type="button"
              className={`weekly-calendar__event weekly-calendar__event--${color}${hasDisciplineCode ? ' weekly-calendar__event--discipline-code' : ''}`}
              style={{ gridColumn: entry.dia_semana + 1, gridRow: `${row} / span ${span}`, alignSelf: 'start', top: `${topInset}%`, height: `calc(${100 - topInset - bottomInset}% - 8px)` }}
              aria-label={`${name}, ${days[entry.dia_semana - 1]}, das ${String(entry.hora_inicio).slice(0, 5)} às ${String(entry.hora_fim).slice(0, 5)}`}
              title={readOnly ? name : `Editar ${name.toLowerCase()}`}
              onClick={() => !readOnly && onSelectEntry?.(entry)}
              disabled={readOnly}
            >
              {eventLabel(entry)}
            </button>
          )
        })}
      </div>

      {footerText !== null && (
        <p>{footerText || 'Toque em um espaço vazio para adicionar ou em uma atividade para editar'}</p>
      )}
    </section>
  )
}

export default ScheduleGrid

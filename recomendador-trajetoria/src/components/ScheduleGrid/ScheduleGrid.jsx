import { weeklyActivityLabel } from '../../utils/weeklyPlan'
import './ScheduleGrid.css'

const days = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
const hours = [8, 10, 12, 14, 16, 18, 20]
const activityColors = {
  DISCIPLINA: 'mint',
  ESTAGIO: 'purple',
  OUTRO: 'pink',
}

function hourValue(value) {
  return Number(String(value).slice(0, 2))
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
  const visibleHours = hours.filter((hour) => hour <= endHour)
  const visibleEntries = entries.filter((entry) => hourValue(entry.hora_inicio) <= endHour)

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
            {String(hour).padStart(2, '0')}
          </span>
        ))}

        {days.flatMap((_, dayIndex) => visibleHours.map((hour, rowIndex) => (
          <button
            key={`${dayIndex + 1}-${hour}`}
            className="weekly-calendar__slot"
            type="button"
            style={{ gridColumn: dayIndex + 2, gridRow: rowIndex + 2 }}
            aria-label={readOnly ? undefined : `Adicionar atividade na ${days[dayIndex]} às ${hour}:00`}
            onClick={() => !readOnly && onSelectSlot?.(dayIndex + 1, hour)}
            disabled={readOnly}
          >
            {!readOnly && <span>+</span>}
          </button>
        )))}

        {visibleEntries.map((entry) => {
          const start = hourValue(entry.hora_inicio)
          const end = hourValue(entry.hora_fim)
          const row = Math.floor((start - 8) / 2) + 2
          const span = Math.max(1, Math.ceil((end - start) / 2))
          const color = entry.cor || activityColors[entry.tipo_atividade] || 'blue'
          const name = eventName(entry)
          const hasDisciplineCode = entry.tipo_atividade === 'DISCIPLINA'
            && Boolean(entry.codigo || entry.disciplina_codigo)

          return (
            <button
              key={entry._key}
              type="button"
              className={`weekly-calendar__event weekly-calendar__event--${color}${hasDisciplineCode ? ' weekly-calendar__event--discipline-code' : ''}`}
              style={{ gridColumn: entry.dia_semana + 1, gridRow: `${row} / span ${span}` }}
              aria-label={`${name}, ${days[entry.dia_semana - 1]}, às ${String(start).padStart(2, '0')} horas`}
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

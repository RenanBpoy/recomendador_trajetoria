import './ScheduleGrid.css'
import { weeklyActivityLabel } from '../../utils/weeklyPlan'

const days = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
const hours = [8, 10, 12, 14, 16, 18, 20]

function hourValue(value) {
  return Number(String(value).slice(0, 2))
}

function ScheduleGrid({ entries = [], onSelectSlot, onSelectEntry }) {
  return (
    <section className="schedule-grid" aria-label="Grade semanal">
      <div className="schedule-grid__days">{days.map((day) => <span key={day}>{day}</span>)}</div>
      <div className="schedule-grid__body">
        <div className="schedule-grid__times">{hours.map((hour) => <span key={hour}>{String(hour).padStart(2, '0')}</span>)}</div>
        <div className="schedule-grid__canvas">
          {days.flatMap((_, dayIndex) => hours.map((hour, rowIndex) => (
            <button
              key={`${dayIndex + 1}-${hour}`}
              className="schedule-slot"
              type="button"
              style={{ gridColumn: dayIndex + 1, gridRow: rowIndex + 1 }}
              aria-label={`Adicionar atividade na ${days[dayIndex]} às ${hour}:00`}
              onClick={() => onSelectSlot?.(dayIndex + 1, hour)}
            ><span>+</span></button>
          )))}
          {entries.map((entry) => {
            const start = hourValue(entry.hora_inicio)
            const end = hourValue(entry.hora_fim)
            const row = Math.floor((start - 8) / 2) + 1
            const span = Math.max(1, Math.ceil((end - start) / 2))
            return (
              <button
                key={entry._key}
                type="button"
                className={`weekly-plan-entry weekly-plan-entry--${entry.tipo_atividade.toLowerCase()}`}
                style={{ gridColumn: entry.dia_semana, gridRow: `${row} / span ${span}` }}
                title="Editar atividade"
                onClick={() => onSelectEntry?.(entry)}
              >
                <strong>{weeklyActivityLabel(entry.tipo_atividade)}</strong>
              </button>
            )
          })}
        </div>
      </div>
      <p>Toque em um espaço vazio para adicionar ou em uma atividade para editar</p>
    </section>
  )
}

export default ScheduleGrid

import { Link } from 'react-router-dom'
import './ScheduleGrid.css'

const entries = [
  { label: 'Cálculo', tone: 'blue', col: 1, row: 1 },
  { label: 'Estágio', tone: 'green', col: 3, row: 1 },
  { label: 'Banco', tone: 'yellow', col: 4, row: 2 },
  { label: 'POO', tone: 'blue', col: 2, row: 4 },
  { label: 'Projeto', tone: 'pink', col: 5, row: 5 },
]

function ScheduleGrid({ selectable = false }) {
  return (
    <section className="schedule-grid" aria-label="Grade semanal">
      <div className="schedule-grid__days"><span>SEG</span><span>TER</span><span>QUA</span><span>QUI</span><span>SEX</span></div>
      <div className="schedule-grid__body">
        <div className="schedule-grid__times"><span>08</span><span>10</span><span>12</span><span>14</span><span>16</span><span>18</span><span>20</span></div>
        <div className="schedule-grid__canvas">
          {entries.map((entry) => (
            <span key={entry.label} className={`schedule-entry schedule-entry--${entry.tone} schedule-entry--c${entry.col} schedule-entry--r${entry.row}`}>{entry.label}</span>
          ))}
          {selectable && <Link to="/horario-disponivel" className="schedule-free"><strong>+</strong><span>Livre</span></Link>}
        </div>
      </div>
      <p>{selectable ? 'Toque em um horário livre para ver opções' : 'Toque em um espaço vazio para adicionar'}</p>
    </section>
  )
}

export default ScheduleGrid

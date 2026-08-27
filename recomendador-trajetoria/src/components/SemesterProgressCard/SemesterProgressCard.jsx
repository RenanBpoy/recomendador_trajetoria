import { Link } from 'react-router-dom'
import './SemesterProgressCard.css'

function SemesterProgressCard({ period, totalDisciplines, totalHours, addedDisciplines }) {
  return (
    <section className="home-semester" aria-labelledby="home-semester-title">
      <header>
        <h2 id="home-semester-title">Semestre em andamento</h2>
        <Link to="/semana">Detalhes</Link>
      </header>
      <div className="home-semester__card">
        <div className="home-semester__summary">
          <span>{period}</span>
          <strong>{totalDisciplines} disciplinas · {totalHours} h</strong>
        </div>
        <div className="home-semester__progress" aria-label={`${addedDisciplines} de ${totalDisciplines} disciplinas adicionadas`}>
          {Array.from({ length: totalDisciplines }, (_, index) => (
            <i key={index} className={index < addedDisciplines ? 'is-done' : ''} />
          ))}
        </div>
        <p><strong>{addedDisciplines} de {totalDisciplines}</strong> disciplinas adicionadas à semana</p>
      </div>
    </section>
  )
}

export default SemesterProgressCard

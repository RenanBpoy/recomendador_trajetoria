import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import './CourseProgressCard.css'

function CourseProgressCard({ percentage, curriculumYear, remainingHours, loading }) {
  const progress = Math.max(0, Math.min(100, Number(percentage) || 0))
  const message = progress >= 50
    ? 'Você já percorreu boa parte do curso.'
    : 'Sua trajetória acadêmica está tomando forma.'

  return (
    <section className="course-progress-card" aria-label="Progresso no curso">
      <div
        className="course-progress-ring"
        style={{ '--course-progress': `${progress * 3.6}deg` }}
        role="img"
        aria-label={`${progress} por cento do curso concluído`}
      >
        <div className="course-progress-ring__center">
          <strong>{loading ? '—' : `${progress}%`}</strong>
          <span>concluído</span>
        </div>
      </div>

      <div className="course-progress-card__content">
        <span className="course-progress-card__tag">
          {curriculumYear ? `CURRÍCULO ${curriculumYear}` : 'CURRÍCULO'}
        </span>
        <h2>{loading ? 'Carregando seu progresso...' : message}</h2>
        <p>{loading ? 'Consultando PPC e histórico escolar.' : `Faltam ${remainingHours} h para concluir sua graduação.`}</p>
        <Link to="/grade">
          Ver trajetória
          <ArrowRight aria-hidden="true" />
        </Link>
      </div>
    </section>
  )
}

export default CourseProgressCard

import { RotateCw } from 'lucide-react'
import { Link } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import ScheduleGrid from '../../components/ScheduleGrid/ScheduleGrid'
import './Semana.css'

function Semana() {
  return (
    <main className="mobile-page week-page">
      <AppHeader title="Monte sua semana" icon={RotateCw} ariaLabel="Reiniciar semana" />
      <div className="week-page__content">
        <div className="schedule-filters">
          <button className="is-active" type="button">+ Disciplina</button>
          <button type="button">+ Estágio</button>
          <button type="button">+ Outro</button>
        </div>

        <ScheduleGrid selectable />

        <section className="planned-load">
          <span>Carga planejada</span>
          <strong>20 h de aula + 20 h de estágio</strong>
        </section>

        <Link className="next-action" to="/horario-disponivel">
          <span><small>Próxima ação</small><strong>Adicionar disciplinas na quarta às 16:00</strong></span>
          <b>›</b>
        </Link>
      </div>
      <BottomNav active="agenda" />
    </main>
  )
}

export default Semana

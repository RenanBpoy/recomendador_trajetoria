import { CalendarDays, CircleUserRound, Grid3X3, ListChecks } from 'lucide-react'
import { Link } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import DailyEvent from '../../components/DailyEvent/DailyEvent'
import MetricStrip from '../../components/MetricStrip/MetricStrip'
import './Home.css'

function Home() {
  return (
    <main className="mobile-page home-page">
      <AppHeader title="Olá, estudante" icon={CircleUserRound} to="/perfil" ariaLabel="Abrir perfil" />
      <div className="home-page__content">
        <section className="semester-summary">
          <span>SEMESTRE ATUAL</span>
          <div><strong>5 disciplinas • 300 h</strong><Link to="/semana">Ver plano</Link></div>
          <p>Risco geral: moderado</p>
        </section>

        <section className="today-section">
          <header><h2>Hoje</h2><Link to="/calendario">Ver agenda</Link></header>
          <div className="today-section__events">
            <DailyEvent time="08:00" title="Cálculo II" detail="Sala 204 • 2 h" />
            <DailyEvent time="14:00" title="Banco de Dados" detail="Laboratório 3 • 2 h" tone="green" />
            <DailyEvent time="18:00" title="Estágio" detail="Empresa • 4 h" tone="yellow" />
          </div>
        </section>

        <section className="quick-actions">
          <h2>Ações rápidas</h2>
          <div>
            <Link to="/grade"><Grid3X3 /><span>Minha grade</span></Link>
            <Link to="/calendario"><CalendarDays /><span>Calendário</span></Link>
            <Link to="/semana"><ListChecks /><span>Meu plano</span></Link>
          </div>
        </section>

        <MetricStrip
          title="Esta semana"
          items={[
            { value: '4', label: 'aulas', tone: 'cyan' },
            { value: '20 h', label: 'carga total', tone: 'green' },
            { value: '1', label: 'prazo', tone: 'yellow' },
          ]}
        />

        <Link className="next-recommendation" to="/horario-disponivel">
          <span><strong>Próxima recomendação</strong><small>Revise sua disponibilidade até sexta-feira.</small></span>
          <b>›</b>
        </Link>
      </div>
      <BottomNav active="início" />
    </main>
  )
}

export default Home

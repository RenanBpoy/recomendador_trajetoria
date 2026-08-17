import { ChevronLeft, ChevronRight, Plus } from 'lucide-react'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import DailyEvent from '../../components/DailyEvent/DailyEvent'
import MetricStrip from '../../components/MetricStrip/MetricStrip'
import './Calendario.css'

const days = Array.from({ length: 31 }, (_, index) => index + 1)

function Calendario() {
  return (
    <main className="mobile-page calendar-page">
      <AppHeader title="Calendário" icon={Plus} ariaLabel="Adicionar evento" />
      <div className="calendar-page__content">
        <div className="calendar-month">
          <strong>Agosto de 2026</strong>
          <span><button type="button" aria-label="Mês anterior"><ChevronLeft size={16} /></button><button type="button" aria-label="Próximo mês"><ChevronRight size={16} /></button></span>
        </div>

        <section className="calendar-card">
          <div className="calendar-weekdays">{['D', 'S', 'T', 'Q', 'Q', 'S', 'S'].map((day, index) => <span key={`${day}-${index}`}>{day}</span>)}</div>
          <div className="calendar-days">
            <i /><i /><i /><i /><i /><i />
            {days.map((day) => (
              <button key={day} type="button" className={day === 5 ? 'is-selected' : ''}>
                {day}
                {[3, 12, 18, 27].includes(day) && <b className="dot green" />}
                {[8, 21].includes(day) && <b className="dot pink" />}
              </button>
            ))}
          </div>
        </section>

        <section className="calendar-events">
          <header><h2>Quarta-feira, 5 de agosto</h2><span>3 eventos</span></header>
          <div>
            <DailyEvent time="08:00" title="Cálculo II" detail="Detalhes e lembrete" />
            <DailyEvent time="14:00" title="Banco de Dados" detail="Detalhes e lembrete" tone="green" />
            <DailyEvent time="19:00" title="Entregar relatório" detail="Detalhes e lembrete" tone="pink" />
          </div>
        </section>

        <MetricStrip
          title="Resumo de agosto"
          items={[
            { value: '12', label: 'aulas', tone: 'cyan' },
            { value: '3', label: 'prazos', tone: 'pink' },
            { value: '2', label: 'provas', tone: 'yellow' },
          ]}
        />
      </div>
      <BottomNav active="agenda" />
    </main>
  )
}

export default Calendario

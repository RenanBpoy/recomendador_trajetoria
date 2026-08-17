import { Check, Clock3, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import './HorarioDisponivel.css'

const suggestions = [
  { title: 'Estruturas de Dados', group: 'TURMA A • QUA 16:00', score: '78%', fit: 'Risco baixo', tone: 'green' },
  { title: 'Redes I', group: 'TURMA B • QUA 16:00', score: '74%', fit: 'Bom encaixe', tone: 'blue' },
  { title: 'Cálculo Numérico', group: 'TURMA C • QUA 16:00', score: '61%', fit: 'Atenção', tone: 'yellow' },
]

function HorarioDisponivel() {
  const navigate = useNavigate()

  return (
    <main className="mobile-page availability-page">
      <AppHeader icon={X} to="/semana" ariaLabel="Fechar sugestões" />
      <div className="availability-page__content">
        <section className="selected-time">
          <span>Horário selecionado</span>
          <strong>Quarta-feira • 16:00 às 18:00</strong>
          <b>Agenda livre</b>
        </section>

        <section className="suggestions">
          <h1>Sugestões para este horário</h1>
          <div>
            {suggestions.map((item) => (
              <article key={item.title} className="suggestion-card">
                <span className="suggestion-card__check"><Check size={17} strokeWidth={3} /></span>
                <div className="suggestion-card__copy">
                  <strong>{item.title}</strong>
                  <small>{item.group}</small>
                  <span className={`small-pill ${item.tone}`}>{item.fit}</span>
                </div>
                <span className="suggestion-card__score">{item.score} <b>›</b></span>
              </article>
            ))}
          </div>
        </section>

        <section className="other-options">
          <h2>Outras opções</h2>
          <button type="button"><span className="green"><Clock3 size={17} /></span><span><strong>Registrar estágio</strong><small>Compromisso recorrente</small></span><b>›</b></button>
          <button type="button"><span className="pink"><X size={18} /></span><span><strong>Bloquear horário</strong><small>Evitar novas sugestões</small></span><b>›</b></button>
        </section>

        <button className="primary-button availability-page__submit" type="button" onClick={() => navigate('/calendario')}>Adicionar à agenda</button>
      </div>
      <BottomNav active="agenda" />
    </main>
  )
}

export default HorarioDisponivel

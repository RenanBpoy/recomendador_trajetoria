import { AlertCircle, ArrowLeft, CalendarX2, Clock3, Gauge, ShieldAlert } from 'lucide-react'
import { Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import { getCurrentRecommendation, hasGeneratedRecommendation } from '../../services/recommendation'
import { useStoredAuth } from '../../hooks/useStoredAuth'
import './TambemAnalisamos.css'

const reasonDetails = {
  CONFLITO_HORARIO: { label: 'Conflito de horário', tone: 'pink', Icon: Clock3 },
  LIMITE_CARGA: { label: 'Limite de carga', tone: 'yellow', Icon: Gauge },
  LIMITE_ALTO_RISCO: { label: 'Limite de alto risco', tone: 'pink', Icon: ShieldAlert },
  SEM_OFERTA_COM_HORARIO: { label: 'Sem oferta compatível', tone: 'blue', Icon: CalendarX2 },
  DISCIPLINA_FUTURA_RISCO_NAO_BAIXO: { label: 'Disciplina futura', tone: 'yellow', Icon: ShieldAlert },
}

function detailFor(code) {
  return reasonDetails[code] || { label: 'Outro critério', tone: 'blue', Icon: AlertCircle }
}

export default function TambemAnalisamos() {
  const auth = useStoredAuth()
  const userId = auth?.usuario?.id || auth?.perfil?.id || ''
  const allowed = hasGeneratedRecommendation(userId)
  const [state, setState] = useState({ data: null, error: '' })
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    if (!allowed) return undefined
    let active = true
    getCurrentRecommendation()
      .then((data) => { if (active) setState({ data, error: '' }) })
      .catch((error) => { if (active) setState({ data: null, error: error.message || 'Não foi possível carregar a análise.' }) })
    return () => { active = false }
  }, [allowed, retry])

  if (!allowed) return <Navigate to="/home" replace />

  const items = state.data?.nao_selecionadas || []

  return (
    <main className="mobile-page also-analyzed-page">
      <AppHeader title="Também analisamos" icon={ArrowLeft} to="/recomendacao" ariaLabel="Voltar para a recomendação" />
      <div className="also-analyzed-page__content">
        <section className="also-analyzed-intro">
          <span>POR TRÁS DA RECOMENDAÇÃO</span>
          <h2>O que ficou fora do plano</h2>
          <p>Estas disciplinas foram consideradas, mas algum critério impediu que entrassem na combinação atual.</p>
        </section>

        {state.error && (
          <section className="also-analyzed-state" role="alert">
            <AlertCircle size={21} />
            <p>{state.error}</p>
            <button type="button" onClick={() => setRetry((current) => current + 1)}>Tentar novamente</button>
          </section>
        )}

        {!state.data && !state.error && <p className="also-analyzed-loading" role="status">Carregando critérios da análise...</p>}

        {state.data && !items.length && (
          <section className="also-analyzed-state also-analyzed-state--success">
            <ListCheckIcon />
            <strong>Nenhuma disciplina ficou de fora</strong>
            <p>A combinação atual acomodou todas as candidatas analisadas.</p>
          </section>
        )}

        {items.length > 0 && (
          <section className="also-analyzed-list" aria-label="Disciplinas não selecionadas">
            <header><strong>{items.length}</strong><span>{items.length === 1 ? 'disciplina analisada' : 'disciplinas analisadas'}</span></header>
            {items.map((item, index) => {
              const { label, tone, Icon } = detailFor(item.motivo_codigo)
              return (
                <article className={`also-analyzed-card also-analyzed-card--${tone}`} key={`${item.disciplina_codigo}-${item.motivo_codigo}-${index}`}>
                  <div className="also-analyzed-card__icon"><Icon size={18} aria-hidden="true" /></div>
                  <div className="also-analyzed-card__content">
                    <span>{item.disciplina_codigo} · {item.semestre_recomendado}º semestre</span>
                    <h3>{item.disciplina_nome}</h3>
                    <strong>{label}</strong>
                    <p>{item.motivo}</p>
                  </div>
                </article>
              )
            })}
          </section>
        )}
      </div>
      <BottomNav />
    </main>
  )
}

function ListCheckIcon() {
  return <span className="also-analyzed-check" aria-hidden="true">✓</span>
}

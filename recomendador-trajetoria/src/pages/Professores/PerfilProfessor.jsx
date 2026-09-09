import { ArrowLeft, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import MetricStrip from '../../components/MetricStrip/MetricStrip'
import { obterProfessor } from '../../services/professores'
import DisciplinaProfessor from './DisciplinaProfessor'
import { taxa } from '../../utils/professores'
import './Professores.css'

export default function PerfilProfessor() {
  const { id } = useParams()
  const [params] = useSearchParams()
  const [state, setState] = useState({ id: null, data: null, error: '' })
  const [retry, setRetry] = useState(0)
  useEffect(() => {
    let active = true
    obterProfessor(id).then((data) => { if (active) setState({ id, data, error: '' }) })
      .catch((err) => { if (active) setState({ id, data: null, error: err.message }) })
    return () => { active = false }
  }, [id, retry])
  const data = state.id === id ? state.data : null
  const error = state.id === id ? state.error : ''
  return (
    <main className="mobile-page professors-page">
      <AppHeader title="Perfil do professor" icon={ArrowLeft} to={`/professores?${params}`} ariaLabel="Voltar à busca de professores" />
      <div className="professors-content">
        {error ? <div role="alert"><p>{error}</p><button className="outline-button" onClick={() => { setState({ id: null, data: null, error: '' }); setRetry((v) => v + 1) }}>Tentar novamente</button></div> : !data ? <p role="status">Carregando perfil...</p> : (
          <>
            <section className="professor-identity">
              <span className="professor-avatar"><UserRound size={48} aria-hidden="true" /></span>
              <span className="professor-eyebrow">Docente · UFSM</span>
              <h2>{data.nome}</h2>
              <p>Resultados dos diários de classe disponíveis</p>
            </section>
            <MetricStrip items={[{ value: data.disciplinas.length, label: 'disciplinas' }, { value: data.total_turmas, label: 'turmas' }, { value: taxa(data.taxa_aprovacao), label: 'aprovação', tone: 'green' }]} />
            <p className="professors-intro">{data.resultados_avaliados} resultados avaliados · {data.outros_resultados} fora do cálculo.</p>
            <h2 className="section-title">Disciplinas ministradas</h2>
            {!data.disciplinas.length && <p className="professors-intro">Ainda não há turmas vinculadas a este professor.</p>}
            {data.disciplinas.map((disciplina) => <DisciplinaProfessor key={disciplina.codigo} disciplina={disciplina} />)}
          </>
        )}
      </div>
      <BottomNav />
    </main>
  )
}

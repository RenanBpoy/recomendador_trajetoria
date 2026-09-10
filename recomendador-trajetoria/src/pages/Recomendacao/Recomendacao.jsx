import { useEffect, useMemo, useState } from 'react'
import { AlertCircle, ArrowLeft, CalendarCheck2, Lightbulb, RefreshCw } from 'lucide-react'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import RecommendationDisciplineCard from '../../components/RecommendationDisciplineCard/RecommendationDisciplineCard'
import ScheduleGrid from '../../components/ScheduleGrid/ScheduleGrid'
import { applyRecommendationToWeeklyPlan } from '../../services/plan'
import { getCurrentRecommendation } from '../../services/recommendation'
import './Recomendacao.css'

const recommendationColors = ['mint', 'purple', 'pink', 'blue', 'amber', 'peach', 'lilac', 'sage']

function Recomendacao() {
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [applyingPlan, setApplyingPlan] = useState(false)
  const [planFeedback, setPlanFeedback] = useState('')
  const [planError, setPlanError] = useState('')

  async function loadRecommendation(force = false) {
    setLoading(true)
    setError('')
    try {
      setRecommendation(await getCurrentRecommendation({ force }))
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível gerar a recomendação.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let active = true
    getCurrentRecommendation()
      .then((data) => active && setRecommendation(data))
      .catch((requestError) => active && setError(
        requestError.message || 'Não foi possível gerar a recomendação.',
      ))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [])

  const disciplines = useMemo(() => (
    (recommendation?.disciplinas || []).map((item, index) => ({
      ...item,
      codigoPpc: item.disciplina_codigo,
      codigo: item.oferta_disciplina_codigo || item.disciplina_codigo,
      nome: item.disciplina_nome,
      risco: item.nivel_risco,
      reprovacao: item.taxa_reprovacao,
      horasSemanais: item.horas_semanais,
      dedicacaoExtraclasse: item.dedicacao_extraclasse,
      justificativa: item.justificativa,
      cor: recommendationColors[index % recommendationColors.length],
    }))
  ), [recommendation])

  const schedule = useMemo(() => disciplines.flatMap((discipline) => (
    discipline.horarios.map((entry) => ({
      _key: `${discipline.oferta_turma_id}-${entry.id}`,
      codigo: discipline.codigo,
      nome_exibicao: discipline.nome,
      tipo_atividade: 'DISCIPLINA',
      dia_semana: entry.dia_semana,
      hora_inicio: entry.hora_inicio,
      hora_fim: entry.hora_fim,
      cor: discipline.cor,
    }))
  )), [disciplines])

  async function applyPlan() {
    setApplyingPlan(true)
    setPlanFeedback('')
    setPlanError('')
    try {
      const result = await applyRecommendationToWeeklyPlan(recommendation)
      setPlanFeedback(result.addedMeetings
        ? `${result.addedDisciplines} disciplina(s) adicionada(s) ao seu plano semanal.`
        : 'As disciplinas recomendadas já estavam no seu plano semanal.')
    } catch (requestError) {
      setPlanError(
        requestError.message
        || 'Não foi possível aplicar a recomendação. Atualize a análise e tente novamente.',
      )
    } finally {
      setApplyingPlan(false)
    }
  }

  return (
    <main className="mobile-page recommendation-page">
      <AppHeader title="Recomendação do Salomão" icon={ArrowLeft} to="/home" ariaLabel="Voltar para o início" />

      <div className="recommendation-page__content">
        {loading && (
          <section className="recommendation-state" aria-live="polite">
            <RefreshCw className="recommendation-state__spinner" size={22} />
            <strong>Analisando sua trajetória...</strong>
            <p>O Salomão está analisando seu PPC, histórico, desempenho e horários.</p>
          </section>
        )}

        {!loading && error && (
          <section className="recommendation-state recommendation-state--error" role="alert">
            <AlertCircle size={22} />
            <strong>Não foi possível montar a análise</strong>
            <p>{error}</p>
            <button type="button" onClick={() => loadRecommendation(true)}>Tentar novamente</button>
          </section>
        )}

        {!loading && !error && recommendation && (
          <>
            <section className="recommendation-summary">
              <div className="recommendation-summary__icon"><Lightbulb size={19} /></div>
              <div>
                <span>RECOMENDAÇÃO INICIAL</span>
                <h2>{recommendation.titulo}</h2>
                <p>{recommendation.mensagem}</p>
              </div>
              <strong>{recommendation.horas_semanais} h/semana</strong>
            </section>

            <section className="recommendation-schedule" aria-labelledby="recommendation-schedule-title">
              <div className="recommendation-section-heading">
                <div>
                  <span>CRONOGRAMA SUGERIDO</span>
                  <h2 id="recommendation-schedule-title">Sua semana</h2>
                </div>
                <small>
                  {recommendation.contexto.ano_alvo}/{recommendation.contexto.semestre_alvo}
                </small>
              </div>
              <ScheduleGrid entries={schedule} readOnly endHour={18} footerText={null} />
              <button
                className="primary-button recommendation-apply-button"
                type="button"
                disabled={applyingPlan || !disciplines.length}
                onClick={applyPlan}
              >
                <CalendarCheck2 size={16} />
                {applyingPlan ? 'Aplicando...' : 'Aplicar plano'}
              </button>
              {planFeedback && <p className="recommendation-plan-feedback is-success" role="status">{planFeedback}</p>}
              {planError && <p className="recommendation-plan-feedback is-error" role="alert">{planError}</p>}
            </section>

            <section className="recommended-disciplines" aria-labelledby="recommended-disciplines-title">
              <div className="recommendation-section-heading">
                <div>
                  <span>ANÁLISE POR DISCIPLINA</span>
                  <h2 id="recommended-disciplines-title">Disciplinas recomendadas</h2>
                </div>
                <small>{disciplines.length} opções</small>
              </div>

              <div className="recommended-disciplines__list">
                {disciplines.map((discipline) => (
                  <RecommendationDisciplineCard key={discipline.codigo} discipline={discipline} />
                ))}
                {!disciplines.length && (
                  <p className="recommendation-empty">
                    Nenhuma combinação compatível foi encontrada para este período.
                  </p>
                )}
              </div>
            </section>

          </>
        )}
      </div>

      <BottomNav />
    </main>
  )
}

export default Recomendacao

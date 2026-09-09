import { BarChart3, BookOpenText, Clock3, Sparkles } from 'lucide-react'
import './RecommendationDisciplineCard.css'

const riskLabels = {
  baixo: 'Baixo risco',
  medio: 'Médio risco',
  alto: 'Alto risco',
  desconhecido: 'Risco sem dados',
}

function RecommendationDisciplineCard({ discipline }) {
  const hasFailureRate = Number.isFinite(discipline.reprovacao)

  return (
    <article className={`recommendation-discipline recommendation-discipline--${discipline.risco} recommendation-discipline--${discipline.cor}`}>
      <div className="recommendation-discipline__heading">
        <div>
          <span>{discipline.codigo}</span>
          <h3>{discipline.nome}</h3>
        </div>
        <strong>{riskLabels[discipline.risco]}</strong>
      </div>

      <div className="recommendation-discipline__metrics">
        <span>
          <BarChart3 size={13} />
          <b>{hasFailureRate ? `${discipline.reprovacao}%` : 'Sem dados'}</b>
          {hasFailureRate ? ' de reprovação' : ' históricos'}
        </span>
        <span><Clock3 size={13} /><b>{discipline.horasSemanais} h</b> por semana</span>
      </div>

      <div
        className="recommendation-discipline__risk"
        aria-label={hasFailureRate ? `${discipline.reprovacao}% de reprovação` : 'Taxa de reprovação indisponível'}
      >
        <span style={{ width: `${hasFailureRate ? discipline.reprovacao : 0}%` }} />
      </div>

      {discipline.dedicacaoExtraclasse && (
        <div className={`recommendation-discipline__dedication recommendation-discipline__dedication--${discipline.dedicacaoExtraclasse.nivel}`}>
          <BookOpenText size={14} aria-hidden="true" />
          <div>
            <strong>{discipline.dedicacaoExtraclasse.titulo}</strong>
            <span>{discipline.dedicacaoExtraclasse.descricao}</span>
          </div>
        </div>
      )}

      <div className="recommendation-discipline__justification">
        <Sparkles size={13} aria-hidden="true" />
        <div>
          <strong>Por que o Salomão recomendou esta disciplina?</strong>
          <p>{discipline.justificativa}</p>
        </div>
      </div>
    </article>
  )
}

export default RecommendationDisciplineCard

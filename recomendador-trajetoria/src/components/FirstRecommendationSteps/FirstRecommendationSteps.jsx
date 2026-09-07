import { ArrowRight, Check, Clock3 } from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  useFirstAccessGuideAction,
  useFirstAccessGuideTarget,
} from '../FirstAccessGuide/FirstAccessGuideContext'
import RecommendationCTA from '../RecommendationCTA/RecommendationCTA'
import './FirstRecommendationSteps.css'

function StepMarker({ number, completed }) {
  return (
    <span className="recommendation-step__marker" aria-label={completed ? `Etapa ${number} concluída` : `Etapa ${number}`}>
      {completed ? <Check size={17} strokeWidth={2.8} /> : number}
    </span>
  )
}

function CurrentStep({ number, title, description, duration, action, to, guideRef, onGuideAction }) {
  const actionContent = <>{action}<ArrowRight size={15} /></>

  return (
    <article className="recommendation-step recommendation-step--current">
      <StepMarker number={number} completed={false} />
      <div className="recommendation-step__content">
        <span className="recommendation-step__eyebrow">ETAPA ATUAL</span>
        <h3>{title}</h3>
        <p>{description}</p>
        <small className="recommendation-step__duration"><Clock3 size={12} />{duration}</small>
        {to ? (
          <Link ref={guideRef} className="recommendation-step__action" to={to} onClick={onGuideAction}>{actionContent}</Link>
        ) : (
          <button className="recommendation-step__action" type="button" disabled title="Funcionalidade em breve">
            {actionContent}
          </button>
        )}
      </div>
    </article>
  )
}

function FirstRecommendationSteps({
  historyLoaded = false,
  checkingHistory = false,
  questionnaireCompleted = false,
  checkingQuestionnaire = false,
  weeklyPlanCompleted = false,
  checkingWeeklyPlan = false,
  onStartRecommendation,
}) {
  const completeGuideAction = useFirstAccessGuideAction()
  const historyGuideRef = useFirstAccessGuideTarget('first-access-history')
  const questionnaireGuideRef = useFirstAccessGuideTarget('first-access-questionnaire')
  const planGuideRef = useFirstAccessGuideTarget('first-access-plan')
  const recommendationGuideRef = useFirstAccessGuideTarget('first-access-recommendation')
  const completedSteps = Number(historyLoaded) + Number(questionnaireCompleted) + Number(weeklyPlanCompleted)
  const percentage = Math.round((completedSteps / 3) * 100)
  const remainingSteps = 3 - completedSteps
  const checking = checkingHistory || checkingQuestionnaire || checkingWeeklyPlan

  return (
    <section className="first-recommendation" aria-labelledby="first-recommendation-title">
      <div className="first-recommendation__topline">
        <span>PRIMEIRO ACESSO</span>
        <small>{checking ? 'Verificando...' : `${completedSteps} de 3 etapas`}</small>
      </div>
      <h2 id="first-recommendation-title">Complete seu perfil acadêmico</h2>
      <p className="first-recommendation__intro">
        {remainingSteps === 0
          ? 'Seu perfil acadêmico está pronto para gerar sua primeira recomendação.'
          : `Faltam ${remainingSteps === 1 ? 'apenas 1 etapa' : `apenas ${remainingSteps} etapas`} para gerar sua primeira recomendação.`}
      </p>

      <div className="first-recommendation__progress" aria-label={`${percentage}% concluído`}>
        <div><span style={{ width: `${percentage}%` }} /></div>
        <small>{percentage}% concluído</small>
      </div>

      <div className="first-recommendation__list">
        {historyLoaded ? (
          <Link
            ref={historyGuideRef}
            className="recommendation-step recommendation-step--completed"
            to="/grade"
            onClick={() => completeGuideAction('open-history')}
          >
            <StepMarker number={1} completed />
            <div className="recommendation-step__content">
              <h3>Histórico acadêmico enviado</h3>
              <p>Seu arquivo já está pronto para análise.</p>
            </div>
            <strong>Concluído</strong>
          </Link>
        ) : (
          <CurrentStep
            guideRef={historyGuideRef}
            number={1}
            title="Envie seu histórico acadêmico"
            description="Precisamos dele para identificar as disciplinas concluídas e pendentes."
            duration="Leva cerca de 1 minuto"
            action="Carregar histórico"
            to="/grade"
            onGuideAction={() => completeGuideAction('open-history')}
          />
        )}

        {questionnaireCompleted ? (
          <Link
            ref={questionnaireGuideRef}
            className="recommendation-step recommendation-step--completed"
            to="/questionario"
            onClick={() => completeGuideAction('open-questionnaire')}
          >
            <StepMarker number={2} completed />
            <div className="recommendation-step__content">
              <h3>Questionário acadêmico respondido</h3>
              <p>Suas respostas pessoais foram salvas.</p>
            </div>
            <strong>Concluído</strong>
          </Link>
        ) : historyLoaded ? (
          <CurrentStep
            guideRef={questionnaireGuideRef}
            number={2}
            title="Conte-nos um pouco sobre você"
            description="Informe seus interesses, objetivos e preferências acadêmicas."
            duration="Leva cerca de 3 minutos"
            action="Preencher questionário"
            to="/questionario"
            onGuideAction={() => completeGuideAction('open-questionnaire')}
          />
        ) : (
          <article className="recommendation-step recommendation-step--upcoming">
            <StepMarker number={2} completed={false} />
            <div className="recommendation-step__content">
              <h3>Conte-nos um pouco sobre você</h3>
              <p>Informe seus interesses, objetivos e preferências acadêmicas.</p>
            </div>
            <strong>Próxima etapa</strong>
          </article>
        )}

        {weeklyPlanCompleted ? (
          <Link
            ref={planGuideRef}
            className="recommendation-step recommendation-step--completed"
            to="/semana"
            onClick={() => completeGuideAction('open-plan')}
          >
            <StepMarker number={3} completed />
            <div className="recommendation-step__content">
              <h3>Disponibilidade definida</h3>
              <p>Seu cronograma semanal foi salvo.</p>
            </div>
            <strong>Concluído</strong>
          </Link>
        ) : historyLoaded && questionnaireCompleted ? (
          <CurrentStep
            guideRef={planGuideRef}
            number={3}
            title="Defina sua disponibilidade"
            description="Escolha os dias, horários e a carga horária desejada."
            duration="Leva cerca de 2 minutos"
            action="Preencher cronograma"
            to="/semana"
            onGuideAction={() => completeGuideAction('open-plan')}
          />
        ) : (
          <article className="recommendation-step recommendation-step--upcoming">
            <StepMarker number={3} completed={false} />
            <div className="recommendation-step__content">
              <h3>Defina sua disponibilidade</h3>
              <p>Escolha os dias, horários e a carga horária desejada.</p>
            </div>
            <strong>Próxima etapa</strong>
          </article>
        )}
      </div>

      <RecommendationCTA
        guideRef={recommendationGuideRef}
        enabled={!checking && completedSteps === 3}
        checking={checking}
        onStart={onStartRecommendation}
      />
    </section>
  )
}

export default FirstRecommendationSteps

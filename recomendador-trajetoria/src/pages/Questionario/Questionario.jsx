import { ArrowLeft, ArrowRight, Info, Sparkles } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AgreementScale from '../../components/AgreementScale/AgreementScale'
import {
  useFirstAccessGuideAction,
  useFirstAccessGuideTarget,
} from '../../components/FirstAccessGuide/FirstAccessGuideContext'
import QuestionnaireHeader from '../../components/QuestionnaireHeader/QuestionnaireHeader'
import QuestionnaireQuestion from '../../components/QuestionnaireQuestion/QuestionnaireQuestion'
import QuestionnaireSection from '../../components/QuestionnaireSection/QuestionnaireSection'
import {
  completeCurrentQuestionnaire,
  getCurrentQuestionnaire,
  saveQuestionnaireAnswer,
} from '../../services/questionnaire'
import './Questionario.css'

function Questionario() {
  const navigate = useNavigate()
  const answerGuideRef = useFirstAccessGuideTarget('first-access-questionnaire-answer')
  const completeGuideAction = useFirstAccessGuideAction()
  const [questionnaire, setQuestionnaire] = useState(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saveState, setSaveState] = useState('')
  const [error, setError] = useState('')

  const questions = useMemo(
    () => questionnaire?.secoes.flatMap((section) => (
      section.perguntas.map((question) => ({ ...question, section }))
    )) || [],
    [questionnaire],
  )
  const currentQuestion = questions[currentIndex]

  useEffect(() => {
    let active = true
    getCurrentQuestionnaire()
      .then((data) => {
        if (!active) return
        setQuestionnaire(data)
        const flattened = data.secoes.flatMap((section) => section.perguntas)
        const firstPending = flattened.findIndex((question) => question.resposta == null)
        setCurrentIndex(firstPending >= 0 ? firstPending : 0)
      })
      .catch((requestError) => {
        if (active) setError(requestError.message || 'Não foi possível carregar o questionário.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => { active = false }
  }, [])

  async function handleAnswer(value) {
    if (!currentQuestion || saving) return
    setSaving(true)
    setError('')
    setSaveState('Salvando resposta...')
    try {
      const saved = await saveQuestionnaireAnswer(currentQuestion.id, value)
      setQuestionnaire(saved)
      setSaveState('Resposta salva automaticamente')
      completeGuideAction('answer-questionnaire')
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível salvar a resposta.')
      setSaveState('')
    } finally {
      setSaving(false)
    }
  }

  async function handleNext() {
    if (!currentQuestion?.resposta || saving) return
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((index) => index + 1)
      setError('')
      return
    }

    setSaving(true)
    setError('')
    setSaveState('Concluindo questionário...')
    try {
      await completeCurrentQuestionnaire()
      navigate('/home', { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível concluir o questionário.')
      setSaveState('')
      const firstPendingId = requestError.details?.perguntas_pendentes?.[0]
      const firstPendingIndex = questions.findIndex((question) => question.id === firstPendingId)
      if (firstPendingIndex >= 0) setCurrentIndex(firstPendingIndex)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="mobile-page questionnaire-page">
        <QuestionnaireHeader />
        <main className="questionnaire-page__state" role="status">Carregando questionário...</main>
      </div>
    )
  }

  if (!questionnaire || !currentQuestion) {
    return (
      <div className="mobile-page questionnaire-page">
        <QuestionnaireHeader />
        <main className="questionnaire-page__state">
          <p role="alert">{error || 'Nenhuma pergunta está disponível no momento.'}</p>
          <button className="outline-button" type="button" onClick={() => navigate('/home')}>Voltar para a Home</button>
        </main>
      </div>
    )
  }

  const currentSection = currentQuestion.section
  const sectionIndex = questionnaire.secoes.findIndex((section) => section.id === currentSection.id)
  const answered = questionnaire.preenchimento.total_respondidas
  const total = questionnaire.preenchimento.total_perguntas
  const percentage = total ? Math.round((answered / total) * 100) : 0

  return (
    <div className="mobile-page questionnaire-page">
      <QuestionnaireHeader />

      <main className="questionnaire-page__content">
        <QuestionnaireSection
          sectionNumber={sectionIndex + 1}
          totalSections={questionnaire.secoes.length}
          title={currentSection.titulo}
          description={currentSection.descricao}
          currentStep={currentQuestion.ordem_secao}
          totalSteps={currentSection.perguntas.length}
        />

        <section className="questionnaire-progress" aria-label="Progresso do questionário">
          <div className="questionnaire-progress__meta">
            <span>{currentSection.titulo.split(' ')[0].toUpperCase()}</span>
            <strong>{currentQuestion.ordem_secao} de {currentSection.perguntas.length}</strong>
          </div>
          <div className="questionnaire-progress__track">
            <span style={{ width: `${percentage}%` }} />
          </div>
          <div className="questionnaire-progress__caption">
            <span>PERGUNTA {currentIndex + 1} DE {total}</span>
            <strong>{percentage}%</strong>
          </div>
        </section>

        <QuestionnaireQuestion number={currentIndex + 1}>
          {currentQuestion.texto}
        </QuestionnaireQuestion>

        <AgreementScale
          guideRef={answerGuideRef}
          selectedValue={currentQuestion.resposta}
          onChange={handleAnswer}
          disabled={saving}
        />

        <aside className="questionnaire-hint">
          <Info size={17} aria-hidden="true" />
          <p>
            {currentSection.orientacao || 'Responda considerando sua experiência atual.'}
          </p>
        </aside>

        <div className="questionnaire-actions">
          <button
            className="outline-button questionnaire-actions__button"
            type="button"
            disabled={currentIndex === 0 || saving}
            onClick={() => setCurrentIndex((index) => Math.max(0, index - 1))}
          >
            <ArrowLeft size={16} />
            Anterior
          </button>
          <button
            className="primary-button questionnaire-actions__button"
            type="button"
            disabled={!currentQuestion.resposta || saving}
            onClick={handleNext}
          >
            {currentIndex === questions.length - 1 ? 'Concluir' : 'Próxima'}
            <ArrowRight size={16} />
          </button>
        </div>

        {error && <p className="questionnaire-page__error" role="alert">{error}</p>}

        <p className="questionnaire-save-note" role="status">
          <Sparkles size={13} aria-hidden="true" />
          {saveState || 'As respostas são salvas automaticamente'}
        </p>
      </main>
    </div>
  )
}

export default Questionario

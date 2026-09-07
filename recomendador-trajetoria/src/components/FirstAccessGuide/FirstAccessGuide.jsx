import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import calendarMascot from '../../assets/img/calendar.png'
import presentingMascot from '../../assets/img/presenting.png'
import thinkingMascot from '../../assets/img/thinking.png'
import uploadMascot from '../../assets/img/upload.png'
import verifiedMascot from '../../assets/img/verified.png'
import MinimizedGuide from './MinimizedGuide'
import { getActiveHistoryImport } from '../../services/academic'
import { getCurrentQuestionnaire } from '../../services/questionnaire'
import { getWeeklyPlan } from '../../services/plan'
import { AUTH_CHANGED_EVENT, getStoredAuth } from '../../services/auth'
import {
  FIRST_ACCESS_GUIDE_CHANGED_EVENT,
  completeFirstAccessGuide,
  shouldShowFirstAccessGuide,
} from '../../services/firstAccessGuide'
import BalaoMascote from '../BalaoMascote/BalaoMascote'
import { FirstAccessGuideContext } from './FirstAccessGuideContext'
import './FirstAccessGuide.css'

const steps = [
  {
    route: '/home',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    imageSrc: presentingMascot,
    text: 'Bem-vindo, estudante! Eu sou o Salomão, o grande sábio, e vou te acompanhar por aqui.',
    nextLabel: 'Vamos lá!',
  },
  {
    route: '/home',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    imageSrc: presentingMascot,
    text: 'Vamos conhecer sua trajetória, entender melhor seu perfil acadêmico e organizar sua semana para preparar sua primeira recomendação.',
    nextLabel: 'Vamos lá!',
  },
  {
    route: '/home',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    showResumePreview: true,
    imageSrc: presentingMascot,
    text: 'Quer fazer uma pausa? Feche o balão no X. Ficarei no canto da tela; toque em mim para continuar de onde parou.',
    nextLabel: 'Continuar',
  },
  {
    route: '/home',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    showResumePreview: true,
    imageSrc: presentingMascot,
    text: 'Se eu estiver no caminho, é só me segurar e arrastar para outro canto da tela.',
    nextLabel: 'Continuar',
  },

  {
    targetId: 'first-access-history',
    actionId: 'open-history',
    route: '/home',
    imageSrc: presentingMascot,
    placement: 'top',
    text: 'Seu histórico mostra o caminho que você já percorreu no curso. Toque em “Carregar histórico” para começarmos por ele.',
  },

  {
    route: '/grade',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    imageSrc: presentingMascot,
    text: 'Esta é a sua grade curricular. Aqui você pode acompanhar o caminho que já percorreu e descobrir o que ainda falta pela frente.',
    nextLabel: 'Carregar meu histórico',
  },

  {
    targetId: 'first-access-history-upload',
    actionId: 'history-uploaded',
    route: '/grade',
    imageSrc: uploadMascot,
    placement: 'top',
    text: 'Envie seu histórico em PDF para atualizar a situação das disciplinas. Depois, você poderá explorar a grade com calma.',
  },

  {
    targetId: 'first-access-home-nav',
    actionId: 'return-home-after-history',
    route: '/grade',
    dimPage: false,
    imageSrc: verifiedMascot,
    placement: 'top',
    text: 'Histórico processado! Dê uma olhada nos semestres e confira como ficou sua trajetória. Quando quiser continuar, toque em “Início”.',
  },

  {
    targetId: 'first-access-questionnaire',
    actionId: 'open-questionnaire',
    route: '/home',
    imageSrc: thinkingMascot,
    placement: 'top',
    text: 'Agora quero conhecer um pouco melhor sua rotina de estudos. Toque aqui para abrir o questionário..',
  },

  {
    route: '/questionario',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    imageSrc: thinkingMascot,
    text: 'As perguntas tratam de rotina, aprendizagem e autonomia. Responda de acordo com a sua experiência; aqui não existem respostas certas ou erradas.',
    nextLabel: 'Responder',
  },

  {
    targetId: 'first-access-questionnaire-answer',
    actionId: 'answer-questionnaire',
    route: '/questionario',
    navigateAfterAction: false,
    imageSrc: thinkingMascot,
    placement: 'bottom',
    text: 'Escolha de 1 a 10 o quanto você concorda com a afirmação. Depois, continue respondendo às próximas perguntas.',
  },

  {
    targetId: 'first-access-plan',
    actionId: 'open-plan',
    route: '/home',
    imageSrc: calendarMascot,
    placement: 'top',
    text: 'Agora quero conhecer um pouco da sua semana. No Plano, você pode me mostrar seus compromissos e horários ocupados para que eu considere tudo isso nas recomendações.',
  },

  {
    route: '/semana',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    imageSrc: calendarMascot,
    text: 'Aqui você organiza aulas, estágio e outros compromissos da semana. Só não vale ocupar das 12h30 às 13h30 — esse é o horário do meu banquete!',
    nextLabel: 'Montar minha semana',
  },

  {
    targetId: 'first-access-plan-grid',
    actionId: 'open-plan-slot',
    route: '/semana',
    imageSrc: calendarMascot,
    placement: 'top',
    text: 'Escolha o tipo de atividade e toque em um horário livre da grade. Assim, vamos encaixar esse compromisso na sua semana.',
  },

  {
    targetId: 'first-access-plan-dialog',
    actionId: 'add-plan-item',
    route: '/semana',
    imageSrc: calendarMascot,
    placement: 'top',
    text: 'Conte um pouco mais sobre essa atividade e confirme para adicioná-la à sua semana.',
  },

  {
    targetId: 'first-access-plan-save',
    actionId: 'save-plan',
    route: '/semana',
    dimPage: false,
    imageSrc: verifiedMascot,
    placement: 'top',
    text: 'Pronto, compromisso adicionado! Agora toque em “Salvar plano” para eu lembrar desses horários na hora de preparar sua recomendação.',
  },

  {
    targetId: 'first-access-recommendation',
    actionId: 'start-recommendation',
    route: '/home',
    imageSrc: verifiedMascot,
    placement: 'top',
    text: 'Tudo pronto! Já conheço sua trajetória, seu perfil e sua semana. Agora é hora de colocar meus bigodes para pensar: toque em “Começar análise” para montarmos sua primeira recomendação.',
  },

  {
    route: '/recomendacao',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    imageSrc: verifiedMascot,
    text: 'Aqui está a sua recomendação! Confira o cronograma e veja por que cada disciplina foi escolhida. Se gostar da proposta, toque em “Aplicar plano” para levá-la ao seu Plano semanal.',
    nextLabel: 'Entendi!',
  },
  {
    route: '/recomendacao',
    standalone: true,
    manualAdvance: true,
    dimPage: false,
    showResumePreview: true,
    imageSrc: presentingMascot,
    text: 'Pronto! Continuarei aqui no cantinho. Afinal, uma jornada de mil disciplinas começa com uma boa escolha... ou algo assim. Se precisar de sabedoria felina, é só chamar o Salomão!',
    nextLabel: 'Concluir guia',
  },
];


function currentUserId() {
  const auth = getStoredAuth()
  return auth?.usuario?.id || auth?.perfil?.id || ''
}

export function FirstAccessGuideProvider({ children }) {
  const navigate = useNavigate()
  const location = useLocation()
  const [userId, setUserId] = useState(currentUserId)
  const [open, setOpen] = useState(() => {
    const id = currentUserId()
    return Boolean(id) && shouldShowFirstAccessGuide(id)
  })
  const [stepIndex, setStepIndex] = useState(0)
  const [minimized, setMinimized] = useState(false)
  const [checking, setChecking] = useState(false)
  const [resumeError, setResumeError] = useState('')
  const [targets, setTargets] = useState({})
  const targetRefCallbacks = useRef(new Map())
  const activeStep = steps[stepIndex]
  const target = activeStep?.targetId ? targets[activeStep.targetId] : null

  const getTargetRef = useCallback((targetId) => {
    if (!targetRefCallbacks.current.has(targetId)) {
      targetRefCallbacks.current.set(targetId, (node) => {
        setTargets((current) => {
          if (current[targetId] === node) return current
          if (!node) {
            const next = { ...current }
            delete next[targetId]
            return next
          }
          return { ...current, [targetId]: node }
        })
      })
    }
    return targetRefCallbacks.current.get(targetId)
  }, [])

  useEffect(() => {
    function syncAuth() {
      const nextUserId = currentUserId()
      setUserId(nextUserId)
      if (nextUserId === userId) return
      setMinimized(false)
      setStepIndex(0)
      setOpen(Boolean(nextUserId) && shouldShowFirstAccessGuide(nextUserId))
    }

    window.addEventListener(AUTH_CHANGED_EVENT, syncAuth)
    return () => window.removeEventListener(AUTH_CHANGED_EVENT, syncAuth)
  }, [userId])

  useEffect(() => {
    function syncGuide(event) {
      if (event.detail?.userId !== userId) return
      if (event.detail.action === 'restart') {
        setStepIndex(0)
        setMinimized(false)
        setOpen(true)
        navigate('/home')
      } else if (event.detail.action === 'complete') {
        setOpen(false)
      }
    }

    window.addEventListener(FIRST_ACCESS_GUIDE_CHANGED_EVENT, syncGuide)
    return () => window.removeEventListener(FIRST_ACCESS_GUIDE_CHANGED_EVENT, syncGuide)
  }, [navigate, userId])

  useEffect(() => {
    if (!open || minimized || !target) return undefined
    const frame = window.requestAnimationFrame(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
    })
    return () => window.cancelAnimationFrame(frame)
  }, [open, minimized, stepIndex, target])

  const finishGuide = useCallback(() => {
    if (userId) completeFirstAccessGuide(userId)
    setOpen(false)
  }, [userId])

  const advanceFromStep = useCallback((currentStep) => {
    if (stepIndex >= steps.length - 1) {
      finishGuide()
      return true
    }

    const nextStep = steps[stepIndex + 1]
    setStepIndex((current) => current + 1)
    if (
      currentStep?.navigateAfterAction !== false
      && !minimized
      && nextStep?.route
      && nextStep.route !== location.pathname
    ) {
      navigate(nextStep.route)
    }
    return true
  }, [finishGuide, location.pathname, navigate, stepIndex, minimized])

  async function resumeGuide() {
    if (checking) return
    const requestedUser = userId
    setChecking(true)
    setResumeError('')
    try {
      const [history, questionnaire, plan] = await Promise.all([
        getActiveHistoryImport({ force: true }),
        getCurrentQuestionnaire({ force: true }),
        getWeeklyPlan({ force: true }),
      ])
      if (currentUserId() !== requestedUser) return
      let next = stepIndex
      const hasHistory = Boolean(history?.id || history?.total_itens)
      const answered = questionnaire?.preenchimento?.status === 'CONCLUIDO'
      const hasPlan = Array.isArray(plan) && plan.length > 0
      const indexOfAction = (action) => steps.findIndex((item) => item.actionId === action)
      const historyUpload = indexOfAction('history-uploaded')
      const historyReturn = indexOfAction('return-home-after-history')
      const questionnaireStart = indexOfAction('open-questionnaire')
      const questionnaireAnswer = indexOfAction('answer-questionnaire')
      const planStart = indexOfAction('open-plan')
      const planSave = indexOfAction('save-plan')
      if (!hasHistory && next > historyUpload) next = indexOfAction('open-history')
      if (hasHistory && next <= historyUpload) next = historyReturn
      if (next === historyReturn && location.pathname !== '/grade') next = questionnaireStart
      if (hasHistory && answered && next <= questionnaireAnswer) next = planStart
      if (hasHistory && !answered && next > questionnaireAnswer) next = questionnaireStart
      if (hasHistory && answered && hasPlan && next <= planSave) next = indexOfAction('start-recommendation')
      if (!hasPlan && next > planSave) next = planStart
      // Um diálogo fechado não pode ser retomado sem selecionar um horário novamente.
      if ((next === indexOfAction('add-plan-item') || next === planSave) && !targets[steps[next].targetId]) next = indexOfAction('open-plan-slot')
      setStepIndex(next)
      navigate(steps[next].route)
      setMinimized(false)
    } catch {
      setResumeError('Não foi possível conferir seu progresso. Toque no gato para tentar novamente.')
    } finally {
      setChecking(false)
    }
  }

  const completeGuideAction = useCallback((actionId) => {
    const currentStep = steps[stepIndex]
    if (!open || currentStep?.actionId !== actionId) return false
    return advanceFromStep(currentStep)
  }, [advanceFromStep, open, stepIndex])

  const advanceGuideStep = useCallback(() => {
    const currentStep = steps[stepIndex]
    if (!open || !currentStep?.manualAdvance) return false
    return advanceFromStep(currentStep)
  }, [advanceFromStep, open, stepIndex])

  useEffect(() => {
    if (!open || minimized || !target || activeStep?.highlightTarget === false) return undefined
    target.classList.add('first-access-guide__target')
    return () => target.classList.remove('first-access-guide__target')
  }, [activeStep?.highlightTarget, open, minimized, target])

  const contextValue = useMemo(
    () => ({ getTargetRef, completeGuideAction }),
    [completeGuideAction, getTargetRef],
  )

  return (
    <FirstAccessGuideContext.Provider value={contextValue}>
      {children}
      {open && !minimized && target && activeStep?.dimPage !== false && (
        <div className="first-access-guide__backdrop" aria-hidden="true" />
      )}
      <BalaoMascote
        target={target}
        open={open && !minimized && location.pathname === activeStep?.route}
        standalone={activeStep?.standalone}
        placement={activeStep?.placement}
        imageSrc={activeStep?.imageSrc}
        text={activeStep?.text}
        nextLabel={activeStep?.nextLabel}
        onNext={activeStep?.manualAdvance ? advanceGuideStep : undefined}
        onClose={() => setMinimized(true)}
        closeLabel="Minimizar guia"
      />
      {(!open || minimized || (activeStep?.showResumePreview && location.pathname === activeStep.route)) && userId && !['/login', '/cadastro', '/'].includes(location.pathname) && (
        <MinimizedGuide
          onResume={open && minimized ? resumeGuide : undefined}
          checking={open && checking}
          error={open ? resumeError : ''}
          label={open ? 'Retomar guia. Segure e arraste para mover.' : 'Salomão. Segure e arraste para mover.'}
        />
      )}
    </FirstAccessGuideContext.Provider>
  )
}

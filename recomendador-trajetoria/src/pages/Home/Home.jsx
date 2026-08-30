import { CircleUserRound, Grid3X3, Sparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import CourseProgressCard from '../../components/CourseProgressCard/CourseProgressCard'
import FirstRecommendationSteps from '../../components/FirstRecommendationSteps/FirstRecommendationSteps'
import MetricStrip from '../../components/MetricStrip/MetricStrip'
import QuickActionCard from '../../components/QuickActionCard/QuickActionCard'
import { useAcademicProgress } from '../../hooks/useAcademicProgress'
import { getActiveHistoryImport } from '../../services/academic'
import { getWeeklyPlan } from '../../services/plan'
import { getCurrentQuestionnaire } from '../../services/questionnaire'
import './Home.css'

function firstName(name) {
  return String(name || 'Estudante').trim().split(/\s+/)[0]
}

function currentAcademicPeriod() {
  const today = new Date()
  return `${today.getFullYear()}/${today.getMonth() < 6 ? 1 : 2}`
}

function Home() {
  const navigate = useNavigate()
  const { profile, curriculum, summary, loading, error } = useAcademicProgress()
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const [checkingHistory, setCheckingHistory] = useState(() => Boolean(profile?.id))
  const [questionnaireCompleted, setQuestionnaireCompleted] = useState(false)
  const [checkingQuestionnaire, setCheckingQuestionnaire] = useState(() => Boolean(profile?.id))
  const [weeklyPlanCompleted, setWeeklyPlanCompleted] = useState(false)
  const [checkingWeeklyPlan, setCheckingWeeklyPlan] = useState(() => Boolean(profile?.id))

  useEffect(() => {
    let active = true
    if (!profile?.id) {
      return () => { active = false }
    }
    getActiveHistoryImport()
      .then((historyImport) => {
        if (active) setHistoryLoaded(Boolean(historyImport?.id || historyImport?.total_itens))
      })
      .catch(() => {
        if (active) setHistoryLoaded(false)
      })
      .finally(() => {
        if (active) setCheckingHistory(false)
      })
    return () => { active = false }
  }, [profile?.id])

  useEffect(() => {
    let active = true
    if (!profile?.id) {
      return () => { active = false }
    }
    getCurrentQuestionnaire()
      .then((questionnaire) => {
        if (active) setQuestionnaireCompleted(questionnaire?.preenchimento?.status === 'CONCLUIDO')
      })
      .catch(() => {
        if (active) setQuestionnaireCompleted(false)
      })
      .finally(() => {
        if (active) setCheckingQuestionnaire(false)
      })
    return () => { active = false }
  }, [profile?.id])

  useEffect(() => {
    let active = true
    if (!profile?.id) {
      return () => { active = false }
    }
    getWeeklyPlan()
      .then((items) => {
        if (active) setWeeklyPlanCompleted(Array.isArray(items) && items.length > 0)
      })
      .catch(() => {
        if (active) setWeeklyPlanCompleted(false)
      })
      .finally(() => {
        if (active) setCheckingWeeklyPlan(false)
      })
    return () => { active = false }
  }, [profile?.id])

  const studentName = firstName(profile?.nome)
  const metrics = [
    { value: String(summary.approved).padStart(2, '0'), label: 'Concluídas', tone: 'green' },
    { value: String(summary.pending).padStart(2, '0'), label: 'Pendentes', tone: 'cyan' },
    { value: String(summary.failed).padStart(2, '0'), label: 'Reprovadas', tone: 'pink' },
  ]

  return (
    <main className="mobile-page home-page">
      <AppHeader title={`Olá, ${studentName}`} icon={CircleUserRound} to="/perfil" ariaLabel="Abrir perfil" />
      <div className="home-page__content">
        <CourseProgressCard
          percentage={summary.percentage}
          curriculumYear={curriculum?.ano_versao}
          remainingHours={summary.remainingHours}
          loading={loading}
        />

        <MetricStrip items={metrics} variant="compact" ariaLabel="Resumo das disciplinas" />

        {error && <p className="home-page__error" role="status">{error}</p>}

        <section className="home-actions" aria-labelledby="home-actions-title">
          <h2 id="home-actions-title">O que você quer fazer?</h2>
          <div className="home-actions__grid">
            <QuickActionCard
              to="/semana"
              icon={Sparkles}
              title="Ver meu plano"
              description={`Sugestões para ${currentAcademicPeriod()}`}
            />
            <QuickActionCard
              to="/grade"
              icon={Grid3X3}
              tone="violet"
              title="Montar grade"
              description="Organize disciplinas e horários"
            />
          </div>
        </section>

        <FirstRecommendationSteps
          historyLoaded={historyLoaded}
          checkingHistory={checkingHistory}
          questionnaireCompleted={questionnaireCompleted}
          checkingQuestionnaire={checkingQuestionnaire}
          weeklyPlanCompleted={weeklyPlanCompleted}
          checkingWeeklyPlan={checkingWeeklyPlan}
          onStartRecommendation={() => navigate('/recomendacao')}
        />

      </div>
      <BottomNav active="início" />
    </main>
  )
}

export default Home

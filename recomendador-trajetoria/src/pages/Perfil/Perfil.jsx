import { Bell, CircleHelp, CircleUserRound, GraduationCap, LockKeyhole, PanelTopClose } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import MetricStrip from '../../components/MetricStrip/MetricStrip'
import { useAcademicProgress } from '../../hooks/useAcademicProgress'
import { listCourseCurricula } from '../../services/academic'
import {
  clearAuthSession,
  updateStoredProfile,
} from '../../services/auth'
import { saveSelectedCurriculum } from '../../services/profile'
import './Perfil.css'

const settings = [
  { title: 'Dados pessoais', subtitle: 'Nome, e-mail e nascimento', icon: CircleUserRound },
  { title: 'Dados acadêmicos', subtitle: 'Curso, matrícula e PPC', icon: GraduationCap },
  { title: 'Notificações', subtitle: 'Aulas, provas e prazos', icon: Bell },
  { title: 'Privacidade', subtitle: 'Dados e permissões', icon: LockKeyhole },
  { title: 'Ajuda e suporte', subtitle: 'Dúvidas sobre o aplicativo', icon: CircleHelp },
]

function courseName(code) {
  if (code === '314') return 'Sistemas de Informação'
  if (code === '307') return 'Ciência da Computação'
  return `Curso ${code || 'não identificado'}`
}

function firstName(name) {
  return String(name || 'Estudante').trim().split(/\s+/)[0]
}

function Perfil() {
  const navigate = useNavigate()
  const { profile, curriculum, summary, loading } = useAcademicProgress()
  const [curricula, setCurricula] = useState([])
  const [selectedPpcId, setSelectedPpcId] = useState(String(profile?.ppc_id || ''))
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    if (!profile?.curso_codigo) return () => { active = false }

    listCourseCurricula(profile.curso_codigo)
      .then((items) => {
        if (!active) return
        setCurricula(items)
        if (!selectedPpcId && items.length === 1) setSelectedPpcId(String(items[0].id))
      })
      .catch((requestError) => {
        if (active) setError(requestError.message || 'Não foi possível carregar os PPCs do curso.')
      })
    return () => { active = false }
  }, [profile?.curso_codigo, selectedPpcId])

  async function handleSavePpc() {
    if (!selectedPpcId) return
    setSaving(true)
    setError('')
    setFeedback('')
    try {
      const updatedProfile = await saveSelectedCurriculum(selectedPpcId)
      updateStoredProfile(updatedProfile)
      setFeedback('PPC salvo. A grade e os progressos já usam essa versão.')
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível salvar o PPC.')
    } finally {
      setSaving(false)
    }
  }

  function handleLogout() {
    clearAuthSession()
    navigate('/login', { replace: true })
  }

  const totalDisciplines = summary.approved + summary.pending + summary.failed

  return (
    <main className="mobile-page profile-page">
      <AppHeader title="Perfil" icon={PanelTopClose} ariaLabel="Abrir menu" />
      <div className="profile-page__content">
        <section className="profile-identity">
          <div className="profile-avatar" />
          <div><h2>{firstName(profile?.nome)}</h2><p>{courseName(profile?.curso_codigo)}</p><span>{profile?.matricula || '—'}</span></div>
        </section>

        <section className="profile-ppc" aria-labelledby="profile-ppc-title">
          <div>
            <span>Currículo utilizado</span>
            <strong id="profile-ppc-title">Escolha seu PPC</strong>
          </div>
          <div className="semester-tabs profile-ppc__tabs" aria-label="Selecionar PPC">
            {curricula.map((item) => (
              <button
                key={item.id}
                type="button"
                className={String(item.id) === selectedPpcId ? 'is-active' : ''}
                aria-pressed={String(item.id) === selectedPpcId}
                onClick={() => {
                  setSelectedPpcId(String(item.id))
                  setFeedback('')
                }}
              >
                {item.ano_versao}
              </button>
            ))}
          </div>
          <button
            className="profile-ppc__save"
            type="button"
            disabled={!selectedPpcId || saving || String(profile?.ppc_id || '') === selectedPpcId}
            onClick={handleSavePpc}
          >
            {saving ? 'Salvando...' : 'Salvar PPC'}
          </button>
          {feedback && <p className="profile-ppc__feedback is-success" role="status">{feedback}</p>}
          {error && <p className="profile-ppc__feedback is-error" role="alert">{error}</p>}
        </section>

        <section className="course-progress">
          <div><span>Progresso no curso</span><strong>{loading ? '...' : `${summary.percentage}% concluído`}</strong></div>
          <div className="progress-track"><span style={{ width: `${summary.percentage}%` }} /></div>
        </section>

        <MetricStrip
          title="Resumo acadêmico"
          items={[
            { value: `${summary.approved}/${totalDisciplines || 0}`, label: 'disciplinas', tone: 'green' },
            { value: String(summary.remainingHours), label: 'horas restantes', tone: 'cyan' },
            { value: curriculum?.ano_versao || '—', label: 'PPC', tone: 'yellow' },
          ]}
        />

        <section className="account-settings">
          <h2>Conta</h2>
          <div>
            {settings.map(({ title, subtitle, icon: Icon }) => (
              <button key={title} type="button">
                <span className="account-settings__icon"><Icon size={15} /></span>
                <span className="account-settings__copy"><strong>{title}</strong><small>{subtitle}</small></span>
                <b>›</b>
              </button>
            ))}
          </div>
        </section>

        <button className="danger-button profile-page__logout" type="button" onClick={handleLogout}>Sair da conta</button>
      </div>
      <BottomNav active="perfil" />
    </main>
  )
}

export default Perfil

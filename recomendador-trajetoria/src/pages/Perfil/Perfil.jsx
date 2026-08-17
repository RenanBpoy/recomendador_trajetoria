import { Bell, CircleHelp, CircleUserRound, GraduationCap, LockKeyhole, PanelTopClose } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import MetricStrip from '../../components/MetricStrip/MetricStrip'
import { clearAuthSession } from '../../services/auth'
import './Perfil.css'

const settings = [
  { title: 'Dados pessoais', subtitle: 'Nome, e-mail e nascimento', icon: CircleUserRound },
  { title: 'Dados acadêmicos', subtitle: 'Curso e matrícula', icon: GraduationCap },
  { title: 'Notificações', subtitle: 'Aulas, provas e prazos', icon: Bell },
  { title: 'Privacidade', subtitle: 'Dados e permissões', icon: LockKeyhole },
  { title: 'Ajuda e suporte', subtitle: 'Dúvidas sobre o aplicativo', icon: CircleHelp },
]

function Perfil() {
  const navigate = useNavigate()

  function handleLogout() {
    clearAuthSession()
    navigate('/login', { replace: true })
  }

  return (
    <main className="mobile-page profile-page">
      <AppHeader title="Perfil" icon={PanelTopClose} ariaLabel="Abrir menu" />
      <div className="profile-page__content">
        <section className="profile-identity">
          <div className="profile-avatar" />
          <div><h2>Renan</h2><p>Sistemas de Informação</p><span>202220227</span></div>
        </section>

        <section className="course-progress">
          <div><span>Progresso no curso</span><strong>68% concluído</strong></div>
          <div className="progress-track"><span /></div>
        </section>

        <MetricStrip
          title="Resumo acadêmico"
          items={[
            { value: '24/36', label: 'disciplinas', tone: 'green' },
            { value: '8,1', label: 'média geral', tone: 'cyan' },
            { value: '6º', label: 'período', tone: 'yellow' },
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

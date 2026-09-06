import { CircleHelp, CircleUserRound, GraduationCap, LockKeyhole, PanelTopClose } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import FormField from '../../components/FormField/FormField'
import MetricStrip from '../../components/MetricStrip/MetricStrip'
import ProfileAvatar from '../../components/ProfileAvatar/ProfileAvatar'
import ProfileDialog from '../../components/ProfileDialog/ProfileDialog'
import { useAcademicProgress } from '../../hooks/useAcademicProgress'
import { useStoredAuth } from '../../hooks/useStoredAuth'
import { listCourseCurricula } from '../../services/academic'
import { clearAuthSession } from '../../services/auth'
import {
  getCurrentProfile,
  requestEmailChange,
  saveSelectedCurriculum,
  updatePassword,
  updatePersonalData,
  uploadAvatar,
} from '../../services/profile'
import './Perfil.css'

const settings = [
  { key: 'personal', title: 'Dados pessoais', subtitle: 'Nome, e-mail e nascimento', icon: CircleUserRound },
  { key: 'academic', title: 'Dados acadêmicos', subtitle: 'Curso, matrícula e PPC', icon: GraduationCap },
  { key: 'privacy', title: 'Privacidade', subtitle: 'Senha de acesso', icon: LockKeyhole },
  { key: 'help', title: 'Ajuda e suporte', subtitle: 'Dúvidas sobre o aplicativo', icon: CircleHelp },
]

function courseName(code) {
  if (code === '314') return 'Sistemas de Informação'
  if (code === '307') return 'Ciência da Computação'
  return `Curso ${code || 'não identificado'}`
}

function firstName(name) {
  return String(name || 'Estudante').trim().split(/\s+/)[0]
}

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

function PerfilPage() {
  const navigate = useNavigate()
  const auth = useStoredAuth()
  const { profile: progressProfile, curriculum, summary, loading } = useAcademicProgress()
  const profile = auth?.perfil || progressProfile
  const [curricula, setCurricula] = useState([])
  const [selectedPpcId, setSelectedPpcId] = useState(() => String(auth?.perfil?.ppc_id || ''))
  const [savingPpc, setSavingPpc] = useState(false)
  const [ppcFeedback, setPpcFeedback] = useState('')
  const [ppcError, setPpcError] = useState('')
  const [activePanel, setActivePanel] = useState(null)
  const [busyAction, setBusyAction] = useState('')
  const [panelFeedback, setPanelFeedback] = useState('')
  const [panelError, setPanelError] = useState('')
  const [avatarBusy, setAvatarBusy] = useState(false)
  const [avatarFeedback, setAvatarFeedback] = useState('')
  const [avatarError, setAvatarError] = useState('')
  const [personalForm, setPersonalForm] = useState({ nome: '', data_nascimento: '' })
  const [email, setEmail] = useState('')
  const [passwordForm, setPasswordForm] = useState({ senha: '', confirmacao_senha: '' })

  useEffect(() => {
    let active = true
    if (!auth?.usuario?.id) return () => { active = false }
    getCurrentProfile()
      .catch((requestError) => {
        if (active) setAvatarError(requestError.message || 'Não foi possível atualizar os dados do perfil.')
      })
    return () => { active = false }
  }, [auth?.usuario?.id])

  useEffect(() => {
    let active = true
    if (!profile?.curso_codigo) return () => { active = false }

    listCourseCurricula(profile.curso_codigo)
      .then((items) => {
        if (!active) return
        setCurricula(items)
        if (!profile?.ppc_id && items.length === 1) setSelectedPpcId(String(items[0].id))
      })
      .catch((requestError) => {
        if (active) setPpcError(requestError.message || 'Não foi possível carregar os PPCs do curso.')
      })
    return () => { active = false }
  }, [profile?.curso_codigo, profile?.ppc_id])

  function openPanel(panel) {
    setPanelFeedback('')
    setPanelError('')
    setActivePanel(panel)
    if (panel === 'personal') {
      setPersonalForm({
        nome: profile?.nome || '',
        data_nascimento: profile?.data_nascimento || '',
      })
      setEmail(auth?.usuario?.email || '')
    }
    if (panel === 'privacy') setPasswordForm({ senha: '', confirmacao_senha: '' })
    if (panel === 'academic') {
      setSelectedPpcId(String(profile?.ppc_id || (curricula.length === 1 ? curricula[0].id : '')))
      setPpcFeedback('')
    }
  }

  async function handleSavePpc() {
    if (!selectedPpcId) return
    setSavingPpc(true)
    setPpcError('')
    setPpcFeedback('')
    try {
      await saveSelectedCurriculum(selectedPpcId)
      setPpcFeedback('PPC salvo. A grade e os progressos já usam essa versão.')
    } catch (requestError) {
      setPpcError(requestError.message || 'Não foi possível salvar o PPC.')
    } finally {
      setSavingPpc(false)
    }
  }

  async function handlePersonalSubmit(event) {
    event.preventDefault()
    setBusyAction('personal')
    setPanelError('')
    setPanelFeedback('')
    try {
      await updatePersonalData(personalForm)
      setPanelFeedback('Nome e data de nascimento atualizados.')
    } catch (requestError) {
      setPanelError(requestError.message || 'Não foi possível atualizar os dados pessoais.')
    } finally {
      setBusyAction('')
    }
  }

  async function handleEmailSubmit(event) {
    event.preventDefault()
    setBusyAction('email')
    setPanelError('')
    setPanelFeedback('')
    try {
      const result = await requestEmailChange(email)
      setPanelFeedback(result.confirmacao_necessaria
        ? 'Enviamos a confirmação para o novo e-mail. O endereço atual continua válido até a confirmação.'
        : 'E-mail atualizado com sucesso.')
    } catch (requestError) {
      setPanelError(requestError.message || 'Não foi possível alterar o e-mail.')
    } finally {
      setBusyAction('')
    }
  }

  async function handlePasswordSubmit(event) {
    event.preventDefault()
    setBusyAction('password')
    setPanelError('')
    setPanelFeedback('')
    try {
      const result = await updatePassword(passwordForm.senha, passwordForm.confirmacao_senha)
      setPasswordForm({ senha: '', confirmacao_senha: '' })
      setPanelFeedback(result.mensagem || 'Senha atualizada com sucesso.')
    } catch (requestError) {
      setPanelError(requestError.message || 'Não foi possível alterar a senha.')
    } finally {
      setBusyAction('')
    }
  }

  async function handleAvatarSelect(file) {
    setAvatarError('')
    setAvatarFeedback('')
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setAvatarError('Escolha uma imagem JPG, PNG ou WebP.')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setAvatarError('A foto deve ter no máximo 5 MB.')
      return
    }
    setAvatarBusy(true)
    try {
      await uploadAvatar(file)
      setAvatarFeedback('Foto do perfil atualizada.')
    } catch (requestError) {
      setAvatarError(requestError.message || 'Não foi possível enviar a foto.')
    } finally {
      setAvatarBusy(false)
    }
  }

  function handleLogout() {
    clearAuthSession()
    navigate('/login', { replace: true })
  }

  const totalDisciplines = summary.approved + summary.pending + summary.failed
  const selectedCurriculum = curricula.find((item) => String(item.id) === String(profile?.ppc_id))

  return (
    <main className="mobile-page profile-page">
      <AppHeader title="Perfil" icon={PanelTopClose} ariaLabel="Abrir menu" />
      <div className="profile-page__content">
        <section className="profile-identity">
          <ProfileAvatar name={profile?.nome} url={profile?.avatar_url} busy={avatarBusy} onSelect={handleAvatarSelect} />
          <div>
            <h2>{firstName(profile?.nome)}</h2>
            <p>{courseName(profile?.curso_codigo)}</p>
            <span>{profile?.matricula || '—'}</span>
            <button type="button" onClick={() => openPanel('personal')}>Editar perfil</button>
          </div>
        </section>
        {avatarFeedback && <p className="profile-page__notice is-success" role="status">{avatarFeedback}</p>}
        {avatarError && <p className="profile-page__notice is-error" role="alert">{avatarError}</p>}

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
            {settings.map(({ key, title, subtitle, icon: Icon }) => (
              <button key={key} type="button" onClick={() => openPanel(key)}>
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

      {activePanel === 'personal' && (
        <ProfileDialog title="Dados pessoais" subtitle="Atualize as informações usadas na sua conta." onClose={() => setActivePanel(null)}>
          <section className="profile-dialog__section">
            <h3>Identificação</h3>
            <form className="profile-dialog__form" onSubmit={handlePersonalSubmit}>
              <FormField label="Nome completo" name="nome" value={personalForm.nome} required onChange={(event) => setPersonalForm((current) => ({ ...current, nome: event.target.value }))} />
              <FormField label="Data de nascimento" type="date" name="data_nascimento" value={personalForm.data_nascimento} max={todayIsoDate()} required onChange={(event) => setPersonalForm((current) => ({ ...current, data_nascimento: event.target.value }))} />
              <button className="profile-dialog__submit" type="submit" disabled={Boolean(busyAction)}>{busyAction === 'personal' ? 'Salvando...' : 'Salvar dados pessoais'}</button>
            </form>
          </section>
          <section className="profile-dialog__section">
            <h3>E-mail de acesso</h3>
            <p>Dependendo da configuração da conta, será necessário confirmar o novo endereço.</p>
            <form className="profile-dialog__form" onSubmit={handleEmailSubmit}>
              <FormField label="E-mail" type="email" name="email" value={email} autoComplete="email" required onChange={(event) => setEmail(event.target.value)} />
              <button className="profile-dialog__submit is-secondary" type="submit" disabled={Boolean(busyAction)}>{busyAction === 'email' ? 'Solicitando...' : 'Alterar e-mail'}</button>
            </form>
          </section>
          {panelFeedback && <p className="profile-dialog__feedback is-success" role="status">{panelFeedback}</p>}
          {panelError && <p className="profile-dialog__feedback is-error" role="alert">{panelError}</p>}
        </ProfileDialog>
      )}

      {activePanel === 'academic' && (
        <ProfileDialog title="Dados acadêmicos" subtitle="Esses dados conectam sua conta à trajetória do curso." onClose={() => setActivePanel(null)}>
          <dl className="profile-dialog__facts">
            <div><dt>Curso</dt><dd>{courseName(profile?.curso_codigo)} ({profile?.curso_codigo || '—'})</dd></div>
            <div><dt>Matrícula</dt><dd>{profile?.matricula || '—'}</dd></div>
            <div><dt>PPC atual</dt><dd>{selectedCurriculum ? `${selectedCurriculum.ano_versao} — ${selectedCurriculum.nome}` : 'Ainda não selecionado'}</dd></div>
          </dl>
          <section className="profile-ppc profile-ppc--dialog" aria-labelledby="profile-ppc-title">
            <div><strong id="profile-ppc-title">Alterar currículo</strong></div>
            <div className="semester-tabs profile-ppc__tabs" role="group" aria-label="Selecionar PPC">
              {curricula.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={String(item.id) === selectedPpcId ? 'is-active' : ''}
                  aria-pressed={String(item.id) === selectedPpcId}
                  disabled={savingPpc}
                  onClick={() => { setSelectedPpcId(String(item.id)); setPpcFeedback('') }}
                >
                  {item.ano_versao}
                </button>
              ))}
            </div>
            <button
              className="profile-dialog__submit"
              type="button"
              disabled={!selectedPpcId || savingPpc || !curricula.length || String(profile?.ppc_id || '') === selectedPpcId}
              onClick={handleSavePpc}
            >
              {savingPpc ? 'Salvando...' : 'Salvar PPC'}
            </button>
            {ppcFeedback && <p className="profile-dialog__feedback is-success" role="status">{ppcFeedback}</p>}
            {ppcError && <p className="profile-dialog__feedback is-error" role="alert">{ppcError}</p>}
          </section>
        </ProfileDialog>
      )}

      {activePanel === 'privacy' && (
        <ProfileDialog title="Privacidade" subtitle="Gerencie a senha de acesso à sua conta." onClose={() => setActivePanel(null)}>
          <section className="profile-dialog__section">
            <h3>Alterar senha</h3>
            <form className="profile-dialog__form" onSubmit={handlePasswordSubmit}>
              <FormField label="Nova senha" type="password" name="senha" value={passwordForm.senha} minLength={8} autoComplete="new-password" required onChange={(event) => setPasswordForm((current) => ({ ...current, senha: event.target.value }))} />
              <FormField label="Confirmar nova senha" type="password" name="confirmacao_senha" value={passwordForm.confirmacao_senha} minLength={8} autoComplete="new-password" required onChange={(event) => setPasswordForm((current) => ({ ...current, confirmacao_senha: event.target.value }))} />
              <button className="profile-dialog__submit" type="submit" disabled={Boolean(busyAction)}>{busyAction === 'password' ? 'Atualizando...' : 'Atualizar senha'}</button>
            </form>
          </section>
          {panelFeedback && <p className="profile-dialog__feedback is-success" role="status">{panelFeedback}</p>}
          {panelError && <p className="profile-dialog__feedback is-error" role="alert">{panelError}</p>}
        </ProfileDialog>
      )}

      {activePanel === 'help' && (
        <ProfileDialog title="Ajuda e suporte" subtitle="Atalhos para as principais ações do recomendador." onClose={() => setActivePanel(null)}>
          <section className="profile-dialog__section profile-help"><h3>Minha grade não reconheceu uma disciplina</h3><p>Abra a grade, envie o histórico escolar e selecione manualmente uma equivalência na disciplina pendente.</p></section>
          <section className="profile-dialog__section profile-help"><h3>O progresso parece incorreto</h3><p>Confira se o PPC selecionado corresponde ao currículo em que você ingressou e se o histórico mais recente foi carregado.</p></section>
          <div className="profile-dialog__actions">
            <button className="profile-dialog__submit" type="button" onClick={() => navigate('/grade')}>Abrir grade</button>
            <button className="profile-dialog__submit is-secondary" type="button" onClick={() => navigate('/')}>Ir para o início</button>
          </div>
        </ProfileDialog>
      )}
    </main>
  )
}

export default PerfilPage

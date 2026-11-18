import { ArrowRight, ExternalLink, LogOut } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import FormField from '../../components/FormField/FormField'
import { beginUfsmLogin, getUfsmLoginConfiguration, login, loginDestination, needsUfsmPortalSignOut, storeAuthSession } from '../../services/auth'
import LoginCampus from './LoginCampus'
import './Login.css'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [loginMode, setLoginMode] = useState('loading')
  const [configurationAttempt, setConfigurationAttempt] = useState(0)
  const [portalUrl, setPortalUrl] = useState(null)
  const [portalSignOutPending, setPortalSignOutPending] = useState(needsUfsmPortalSignOut)
  const [portalOpened, setPortalOpened] = useState(false)
  const institutional = loginMode === 'ufsm'

  useEffect(() => {
    let active = true
    getUfsmLoginConfiguration().then((config) => {
      if (active) {
        setLoginMode(config?.habilitado ? 'ufsm' : 'legacy')
        setPortalUrl(config?.url_portal ?? null)
      }
    }).catch(() => {
      if (active) setLoginMode('unavailable')
    })
    return () => { active = false }
  }, [configurationAttempt])

  async function handleSubmit(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setError('')
    setSubmitting(true)

    try {
      if (institutional) {
        if (needsUfsmPortalSignOut() && !portalOpened) {
          setPortalSignOutPending(true)
          return
        }
        await beginUfsmLogin(location.state?.from)
        return
      }
      const result = await login({ email: form.get('email'), senha: form.get('password') })
      if (!storeAuthSession(result)) throw new Error('O servidor não retornou uma sessão válida.')
      navigate(loginDestination(location.state?.from), { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível entrar na sua conta.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="mobile-page login-page login-page--campus">
      <div className={institutional ? 'login-page__hero login-page__hero--portal' : 'login-page__hero'}>
        {!institutional && (
          <header className="login-page__campus-brand">
            <span>Salomão</span>
            <small>UFSM</small>
          </header>
        )}
        <LoginCampus>
          {institutional && (
            <section className="login-page__campus-copy login-page__portal-copy" aria-labelledby="login-title">
              <p className="login-page__campus-label">UFSM</p>
              <h1 id="login-title">Salomão</h1>
              <p className="login-page__campus-description">Faça login para abrir seu planejamento</p>
            </section>
          )}
          {institutional && !portalSignOutPending && (
            <form className="login-campus__entry" onSubmit={handleSubmit}>
              <button className="login-campus__gate" type="submit" disabled={submitting} aria-busy={submitting}>
                <ArrowRight size={20} aria-hidden="true" />
                {submitting ? 'Entrando…' : 'Entrar pela UFSM'}
              </button>
            </form>
          )}
        </LoginCampus>
      </div>

      <div className="login-page__campus-copy">
        {institutional && portalSignOutPending && (
          <section className="login-page__portal-signout" aria-labelledby="portal-signout-title">
            <header className="portal-signout__header">
              <span className="portal-signout__icon" aria-hidden="true"><LogOut size={20} /></span>
              <div>
                <p className="portal-signout__eyebrow">Sessão institucional</p>
                <h2 id="portal-signout-title">Encerre a sessão na UFSM</h2>
              </div>
            </header>
            <p className="portal-signout__description">
              A UFSM pode manter sua conta conectada. No portal, clique em <strong>Sair</strong> se a sessão ainda estiver aberta e volte para entrar novamente.
            </p>
            {portalUrl ? (
              <a className={portalOpened ? 'outline-button' : 'primary-button'} href={portalUrl} target="_blank" rel="noopener noreferrer" onClick={() => setPortalOpened(true)}>
                Abrir portal da UFSM <ExternalLink size={15} aria-hidden="true" />
              </a>
            ) : (
              <p className="form-feedback is-error" role="alert">O endereço do portal não foi retornado. Recarregue a página após atualizar o backend.</p>
            )}
            {portalOpened && (
              <form onSubmit={handleSubmit}>
                <button className="primary-button" type="submit" disabled={submitting} aria-busy={submitting}>
                  {submitting ? 'Entrando…' : 'Já saí da UFSM. Entrar'}
                  {!submitting && <ArrowRight size={16} aria-hidden="true" />}
                </button>
              </form>
            )}
          </section>
        )}
        {!institutional && (
          <>
            <p className="login-page__campus-label">Trajetória Acadêmica</p>
            <h1 id="login-title">Planeje seu próximo semestre</h1>
            <p className="login-page__campus-description">
              Consulte sua grade, organize seus horários e descubra quais disciplinas combinam com sua rotina.
            </p>
          </>
        )}

        {(institutional || loginMode === 'legacy') && location.state?.message && (
          <p className="form-feedback is-success" role="status">{location.state.message}</p>
        )}
        {error && <p className="form-feedback is-error" role="alert">{error}</p>}
        {loginMode === 'loading' && <p className="login-page__status" role="status">Carregando opções de acesso…</p>}
        {loginMode === 'unavailable' && (
          <div className="login-form">
            <p className="form-feedback is-error" role="alert">Não foi possível carregar as opções de acesso.</p>
            <button className="primary-button" type="button" onClick={() => {
              setLoginMode('loading')
              setConfigurationAttempt((attempt) => attempt + 1)
            }}>Tentar novamente</button>
          </div>
        )}
        {loginMode === 'legacy' && <>
          <form className="login-form" onSubmit={handleSubmit}>
            <FormField label="E-mail" name="email" type="email" placeholder="seuemail@universidade.br" autoComplete="email" defaultValue={location.state?.email || ''} required />
            <FormField label="Senha" name="password" type="password" placeholder="••••••••" autoComplete="current-password" required />
            <Link className="login-form__forgot" to="/login">Esqueci minha senha</Link>
            <button className="primary-button" type="submit" disabled={submitting} aria-busy={submitting}>
              {submitting ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
          <div className="login-page__signup">
            <span>Ainda não possui conta?</span>
            <Link to="/cadastro">Criar cadastro</Link>
          </div>
        </>}
      </div>
    </main>
  )
}

export default Login

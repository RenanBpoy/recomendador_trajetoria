import { Home as HomeIcon } from 'lucide-react'
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import FormField from '../../components/FormField/FormField'
import { login, storeAuthSession } from '../../services/auth'
import './Login.css'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    const form = new FormData(event.currentTarget)

    try {
      const result = await login({
        email: form.get('email'),
        senha: form.get('password'),
      })
      storeAuthSession(result)

      const previousRoute = location.state?.from
      const destination = previousRoute && !['/login', '/cadastro'].includes(previousRoute)
        ? previousRoute
        : '/home'
      navigate(destination, { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível entrar na sua conta.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="mobile-page login-page">
      <span className="login-page__brand">TCC</span>
      <div className="login-page__mark" aria-hidden="true"><HomeIcon size={27} strokeWidth={2.7} /></div>

      <form className="login-form" onSubmit={handleSubmit}>
        {location.state?.message && <p className="form-feedback is-success" role="status">{location.state.message}</p>}
        {error && <p className="form-feedback is-error" role="alert">{error}</p>}
        <FormField label="E-mail" name="email" type="email" placeholder="seuemail@universidade.br" autoComplete="email" defaultValue={location.state?.email || ''} required />
        <FormField label="Senha" name="password" type="password" placeholder="••••••••" autoComplete="current-password" required />
        <Link className="login-form__forgot" to="/login">Esqueci minha senha</Link>
        <button className="primary-button login-form__submit" type="submit" disabled={submitting} aria-busy={submitting}>
          {submitting ? 'Entrando...' : 'Entrar'}
        </button>
      </form>

      <div className="login-page__signup">
        <span>Ainda não possui conta?</span>
        <Link to="/cadastro">Criar cadastro</Link>
      </div>
    </main>
  )
}

export default Login

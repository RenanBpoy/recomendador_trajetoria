import { ArrowLeft, CalendarDays } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import FormField from '../../components/FormField/FormField'
import { signup, storeAuthSession } from '../../services/auth'
import './Cadastro.css'

function normalizeBirthdate(value) {
  const normalized = value.trim()
  if (/^\d{4}-\d{2}-\d{2}$/.test(normalized)) return normalized

  const match = normalized.match(/^(\d{2})\/(\d{2})\/(\d{4})$/)
  if (!match) throw new Error('Informe a data de nascimento no formato dd/mm/aaaa.')

  const [, day, month, year] = match
  const parsed = new Date(`${year}-${month}-${day}T00:00:00Z`)
  if (
    Number.isNaN(parsed.getTime())
    || parsed.getUTCFullYear() !== Number(year)
    || parsed.getUTCMonth() + 1 !== Number(month)
    || parsed.getUTCDate() !== Number(day)
  ) {
    throw new Error('Informe uma data de nascimento válida.')
  }
  return `${year}-${month}-${day}`
}

function Cadastro() {
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    const form = new FormData(event.currentTarget)
    const password = form.get('password')
    const passwordConfirmation = form.get('password-confirmation')

    if (password !== passwordConfirmation) {
      setError('A confirmação de senha não corresponde à senha.')
      return
    }

    setSubmitting(true)
    try {
      const email = form.get('email')
      const result = await signup({
        nome: form.get('name'),
        matricula: form.get('registration'),
        email,
        data_nascimento: normalizeBirthdate(form.get('birthdate')),
        curso_codigo: form.get('course'),
        senha: password,
        confirmacao_senha: passwordConfirmation,
        aceitou_termos: form.get('terms') === 'on',
      })

      if (storeAuthSession(result)) {
        navigate('/home', { replace: true })
        return
      }

      navigate('/login', {
        replace: true,
        state: {
          email,
          message: result.confirmacao_email_necessaria
            ? 'Cadastro realizado. Confirme seu e-mail antes de entrar.'
            : 'Cadastro realizado. Agora você já pode entrar.',
        },
      })
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível criar sua conta.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="mobile-page cadastro-page">
      <AppHeader title="Crie sua conta" icon={ArrowLeft} to="/login" ariaLabel="Voltar para o login" />
      <form className="cadastro-form" onSubmit={handleSubmit}>
        {error && <p className="form-feedback is-error" role="alert">{error}</p>}
        <FormField label="Nome completo" name="name" placeholder="Digite seu nome" autoComplete="name" required />
        <FormField label="Matrícula" name="registration" placeholder="Ex.: 202312345" inputMode="numeric" required />
        <FormField label="E-mail" name="email" type="email" placeholder="seuemail@universidade.br" autoComplete="email" required />
        <div className="cadastro-form__row">
          <FormField label="Data de nascimento" name="birthdate" placeholder="dd/mm/aaaa" icon={CalendarDays} autoComplete="bday" inputMode="numeric" required />
          <label className="select-field">
            <span>Curso</span>
            <select name="course" defaultValue="" required>
              <option value="" disabled>Selecione</option>
              <option value="314">Sistemas de Informação</option>
              <option value="307">Ciência da Computação</option>
            </select>
          </label>
        </div>
        <FormField label="Senha" name="password" type="password" placeholder="Crie uma senha segura" autoComplete="new-password" minLength={8} required />
        <FormField label="Confirmar senha" name="password-confirmation" type="password" placeholder="Repita a senha" autoComplete="new-password" minLength={8} required />

        <label className="terms-check">
          <input type="checkbox" name="terms" required />
          <span>Concordo com os termos e a política de privacidade.</span>
        </label>

        <button className="primary-button cadastro-form__submit" type="submit" disabled={submitting} aria-busy={submitting}>
          {submitting ? 'Criando conta...' : 'Criar conta'}
        </button>
        <Link className="cadastro-form__login" to="/login">Já possui conta? Entrar</Link>
      </form>
    </main>
  )
}

export default Cadastro

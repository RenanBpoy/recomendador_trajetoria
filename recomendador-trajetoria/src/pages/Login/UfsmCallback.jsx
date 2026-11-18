import { ShieldCheck } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { completeUfsmLogin, confirmUfsmLogin, requestUfsmPortalSignOut, storeAuthSession } from '../../services/auth'
import './Login.css'
import './UfsmCallback.css'

export default function UfsmCallback() {
  const navigate = useNavigate()
  const operation = useRef(null)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [selected, setSelected] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const options = result?.pending.vinculos ?? []
  const multiple = options.length > 1
  const bindingId = multiple ? selected : options[0]?.id

  useEffect(() => {
    let active = true
    // React pode executar o efeito duas vezes em desenvolvimento. O código
    // da UFSM é de uso único, então ambas observam a mesma troca.
    operation.current ??= completeUfsmLogin()
    operation.current.then((value) => {
      if (active) setResult(value)
    }).catch((requestError) => {
      if (active) setError(requestError.message || 'Não foi possível entrar pela UFSM.')
    })
    return () => { active = false }
  }, [])

  async function handleConfirm(event) {
    event.preventDefault()
    if (!bindingId || submitting) return
    setSubmitting(true)
    try {
      const auth = await confirmUfsmLogin(result.pending.confirmacao, bindingId)
      if (!storeAuthSession(auth)) throw new Error('O servidor não retornou uma sessão válida.')
      navigate(result.destination, { replace: true })
    } catch (requestError) {
      setResult(null)
      setError(requestError.message || 'Não foi possível entrar pela UFSM.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="mobile-page login-page">
      <span className="login-page__brand">Salomão</span>
      <section className="ufsm-callback" aria-labelledby="ufsm-callback-title">
        <header className="ufsm-callback__header">
          <span className="ufsm-callback__icon" aria-hidden="true"><ShieldCheck size={28} /></span>
          <p className="ufsm-callback__kicker">ACESSO INSTITUCIONAL</p>
          <h1 id="ufsm-callback-title">{error ? 'Não foi possível entrar' : result ? 'Confirme seu acesso' : 'Concluindo seu login'}</h1>
          {!error && !result && <p role="status">Estamos confirmando seu acesso com a UFSM.</p>}
          {result && <p>Conta autenticada: <strong>{result.pending.nome}</strong></p>}
        </header>
        {error && <>
          <p className="form-feedback is-error" role="alert">{error}</p>
          <Link className="primary-button" to="/login" replace>Voltar ao login</Link>
        </>}
        {result && (
          <form className="ufsm-callback__form" onSubmit={handleConfirm} aria-busy={submitting}>
            {multiple ? (
              <fieldset className="ufsm-callback__bindings" disabled={submitting}>
                <legend>Qual vínculo você quer acessar?</legend>
                {options.map((binding) => (
                  <label className="ufsm-callback__binding" key={binding.id}>
                    <input type="radio" name="vinculo" checked={selected === binding.id} onChange={() => setSelected(binding.id)} />
                    <span>
                      <strong>{binding.curso_nome || `Curso ${binding.curso_codigo}`}</strong>
                      <small>Matrícula {binding.matricula}</small>
                    </span>
                  </label>
                ))}
              </fieldset>
            ) : (
              <p className="ufsm-callback__single">
                {options[0].curso_nome || `Curso ${options[0].curso_codigo}`} · Matrícula {options[0].matricula}
              </p>
            )}
            <button className="primary-button" type="submit" disabled={!bindingId || submitting}>
              {submitting ? 'Entrando…' : 'Continuar'}
            </button>
            {!submitting && <Link className="ufsm-callback__back" to="/login" replace onClick={requestUfsmPortalSignOut}>Trocar de conta</Link>}
          </form>
        )}
      </section>
    </main>
  )
}

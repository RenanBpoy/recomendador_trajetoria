import { ArrowLeft, ChevronRight, Search, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import AppHeader from '../../components/AppHeader/AppHeader'
import BottomNav from '../../components/BottomNav/BottomNav'
import FormField from '../../components/FormField/FormField'
import { buscarProfessores } from '../../services/professores'
import './Professores.css'

export default function Professores() {
  const [params, setParams] = useSearchParams()
  const nome = params.get('nome') || ''
  const [draft, setDraft] = useState(nome)
  const [page, setPage] = useState(0)
  const [result, setResult] = useState({ itens: [], tem_mais: false })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)
  useEffect(() => {
    let active = true
    buscarProfessores(nome, page * 30).then((data) => {
      if (active) { setResult(data); setError(''); setLoading(false) }
    }).catch((err) => { if (active) { setError(err.message); setLoading(false) } })
    return () => { active = false }
  }, [nome, page, retry])
  function search(event) {
    event.preventDefault()
    setLoading(true); setError(''); setPage(0); setParams(draft.trim() ? { nome: draft.trim() } : {}); setRetry((value) => value + 1)
  }
  return (
    <main className="mobile-page professors-page">
      <AppHeader title="Professores" icon={ArrowLeft} to="/home" ariaLabel="Voltar ao início" />
      <div className="professors-content">
        <p className="professors-intro">Conheça as disciplinas e os resultados das turmas de cada professor.</p>
        <form className="professors-search" onSubmit={search}>
          <FormField label="Nome do professor" name="professor" placeholder="Quem você procura?" value={draft} maxLength={120} onChange={(event) => setDraft(event.target.value)} />
          <button className="primary-button" type="submit" disabled={loading}><Search size={17} />Pesquisar</button>
        </form>
        {loading ? <p role="status">Buscando professores...</p> : error ? <div role="alert"><p>{error}</p><button className="outline-button" onClick={() => { setLoading(true); setRetry((v) => v + 1) }}>Tentar novamente</button></div> : (
          <>
            {!result.itens.length && <p className="professors-intro">Nenhum professor encontrado. Tente uma parte do nome.</p>}
            <ul className="professors-list">{result.itens.map((professor) => (
              <li key={professor.id}><Link to={`/professores/${professor.id}${nome ? `?nome=${encodeURIComponent(nome)}` : ''}`}>
                <span className="professor-avatar professor-avatar--small"><UserRound size={22} aria-hidden="true" /></span>
                <span><strong>{professor.nome}</strong><small>Ver disciplinas e turmas</small></span><ChevronRight size={18} aria-hidden="true" />
              </Link></li>
            ))}</ul>
            {(page > 0 || result.tem_mais) && <nav className="professors-pagination" aria-label="Páginas de professores">
              <button className="outline-button" disabled={!page} onClick={() => { setLoading(true); setPage(page - 1) }}>Anterior</button>
              <span>{page + 1}</span>
              <button className="outline-button" disabled={!result.tem_mais} onClick={() => { setLoading(true); setPage(page + 1) }}>Próxima</button>
            </nav>}
          </>
        )}
      </div>
      <BottomNav />
    </main>
  )
}

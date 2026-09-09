import { BookOpen, ChevronRight, Search } from 'lucide-react'
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import FormField from '../../components/FormField/FormField'
import ConsultaLayout, { ConsultaEstado } from '../../components/ConsultaAcademica/ConsultaLayout'
import { useConsultaAcademica } from '../../hooks/useConsultaAcademica'

export default function Disciplinas({ diarios = false }) {
  const [params, setParams] = useSearchParams()
  const busca = params.get('busca') || ''
  const inicio = Math.max(0, Number(params.get('inicio')) || 0)
  const [draft, setDraft] = useState(busca)
  const path = `/consultas/disciplinas?${new URLSearchParams({ busca, inicio, limite: 30 })}`
  const { data, error, retry } = useConsultaAcademica(path)
  const base = diarios ? '/diarios-classe/disciplina' : '/disciplinas'
  return <ConsultaLayout title={diarios ? 'Diários de classe' : 'Disciplinas'}>
    <p className="professors-intro">{diarios ? 'Primeiro escolha a disciplina. Depois, selecione o ano, semestre e turma do diário.' : 'Busque pelo nome ou código para conhecer a disciplina e os resultados das turmas.'}</p>
    <form className="professors-search" onSubmit={(event) => { event.preventDefault(); setParams({ busca: draft.trim() }); if (busca === draft.trim() && !inicio) retry() }}>
      <FormField label="Nome ou código da disciplina" name="disciplina" placeholder="Ex.: Sistemas Operacionais ou ELC1080" value={draft} maxLength={120} onChange={(event) => setDraft(event.target.value)} />
      <button type="submit" className="primary-button"><Search size={17} />Pesquisar</button>
    </form>
    {!data ? <ConsultaEstado error={error} retry={retry} /> : <>
      {!data.itens.length && <p>Nenhuma disciplina encontrada. Tente outra parte do nome.</p>}
      <ul className="professors-list">{data.itens.map((item) => <li key={item.codigo}><Link to={`${base}/${encodeURIComponent(item.codigo)}`}><span className="professor-avatar professor-avatar--small"><BookOpen size={21} /></span><span><strong>{item.nome}</strong><small>{item.codigo}</small></span><ChevronRight size={18} /></Link></li>)}</ul>
      {(inicio > 0 || data.tem_mais) && <nav className="professors-pagination" aria-label="Páginas de disciplinas"><button className="outline-button" disabled={!inicio} onClick={() => setParams({ busca, inicio: Math.max(0, inicio - 30) })}>Anterior</button><span>{Math.floor(inicio / 30) + 1}</span><button className="outline-button" disabled={!data.tem_mais} onClick={() => setParams({ busca, inicio: inicio + 30 })}>Próxima</button></nav>}
    </>}
  </ConsultaLayout>
}

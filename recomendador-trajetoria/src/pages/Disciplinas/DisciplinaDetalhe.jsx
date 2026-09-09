import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ConsultaLayout, { ConsultaEstado } from '../../components/ConsultaAcademica/ConsultaLayout'
import ResumoResultados from '../../components/ConsultaAcademica/ResumoResultados'
import { useConsultaAcademica } from '../../hooks/useConsultaAcademica'

export default function DisciplinaDetalhe({ diarios = false }) {
  const { codigo } = useParams()
  const { data, error, retry } = useConsultaAcademica(`/consultas/disciplinas/${encodeURIComponent(codigo)}`)
  const [periodo, setPeriodo] = useState('')
  const periodos = [...new Set(data?.turmas.map((t) => `${t.ano}/${t.semestre}`) || [])]
  return <ConsultaLayout title={diarios ? 'Escolha a turma' : 'Sobre a disciplina'} back={diarios ? '/diarios-classe' : '/disciplinas'}>
    {!data ? <ConsultaEstado error={error} retry={retry} /> : <>
      <section className="professor-identity"><span className="professor-eyebrow">{data.codigo}</span><h2>{data.nome}</h2><p>{data.cargas_horarias.length ? `${data.cargas_horarias.join(' / ')} h registradas nas ofertas` : 'Carga horária não disponível nos diários'}</p></section>
      {!diarios && <ResumoResultados data={data} />}
      <h2 className="section-title">Diários das turmas</h2>
      {periodos.length > 0 && <label className="consulta-select">Ano e semestre<select value={periodo} onChange={(event) => setPeriodo(event.target.value)}><option value="">Todos os períodos</option>{periodos.map((p) => <option key={p}>{p}</option>)}</select></label>}
      {!data.turmas.length && <p className="professors-intro">Nenhum diário de classe cadastrado para esta disciplina.</p>}
      <ul className="professors-list">{data.turmas.filter((t) => !periodo || `${t.ano}/${t.semestre}` === periodo).map((turma) => <li key={turma.id}><Link to={`/diarios-classe/${turma.id}`}><span><strong>{turma.ano}/{turma.semestre} · Turma {turma.codigo_turma}</strong><small>{turma.curso_codigo === '314' ? 'Sistemas de Informação' : turma.curso_codigo === '307' ? 'Ciência da Computação' : `Curso ${turma.curso_codigo}`} · {turma.carga_horaria} h</small></span><span aria-hidden="true">›</span></Link></li>)}</ul>
    </>}
  </ConsultaLayout>
}

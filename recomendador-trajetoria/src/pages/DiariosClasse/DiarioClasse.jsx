import { Link, useParams } from 'react-router-dom'
import ConsultaLayout, { ConsultaEstado } from '../../components/ConsultaAcademica/ConsultaLayout'
import ResumoResultados from '../../components/ConsultaAcademica/ResumoResultados'
import { useConsultaAcademica } from '../../hooks/useConsultaAcademica'

const nota = (value) => value == null ? '—' : value.toLocaleString('pt-BR')

export default function DiarioClasse() {
  const { id } = useParams()
  const { data, error, retry } = useConsultaAcademica(`/diarios-classe/${encodeURIComponent(id)}`)
  const oferta = data?.oferta
  return <ConsultaLayout title="Diário de classe" back={oferta ? `/diarios-classe/disciplina/${oferta.disciplina_codigo}` : '/diarios-classe'}>
    {!data ? <ConsultaEstado error={error} retry={retry} /> : <>
      <section className="professor-identity"><span className="professor-eyebrow">{oferta.disciplina_codigo} · {oferta.ano}/{oferta.semestre}</span><h2>{oferta.disciplina_nome}</h2><p>Turma {oferta.codigo_turma} · {oferta.curso_nome}</p></section>
      <dl className="consulta-facts"><div><dt>Carga horária</dt><dd>{oferta.carga_horaria} h</dd></div><div><dt>Créditos</dt><dd>{oferta.creditos}</dd></div><div><dt>Situação</dt><dd>{oferta.situacao}</dd></div></dl>
      <section className="consulta-section"><h2 className="section-title">Professores da turma</h2>{oferta.docentes.length ? <ul>{oferta.docentes.map((d) => <li key={d.id}><Link to={`/professores/${d.id}`}>{d.nome} ›</Link></li>)}</ul> : <p>Docente não informado no diário.</p>}</section>
      <ResumoResultados data={data} explicar={false} />
      <section className="consulta-section"><h2 className="section-title">Registros da turma</h2>
        {!data.registros.length ? <p>Nenhum registro disponível para esta consulta.</p> : <div className="consulta-table" tabIndex={0} role="region" aria-label="Registros do diário, deslize para ver todas as colunas"><table><caption>Notas e frequência registradas no banco</caption><thead><tr><th>Nº</th><th>Aluno</th><th>Matrícula</th><th>Curso</th><th>Média parcial</th><th>Média final</th><th>Faltas</th><th>Situação</th></tr></thead><tbody>{data.registros.map((r) => <tr key={`${r.matricula}-${r.numero_lista}`}><td>{r.numero_lista}</td><th scope="row">{r.nome}</th><td>{r.matricula}</td><td>{r.curso_aluno_codigo}</td><td>{nota(r.media_parcial)}</td><td>{nota(r.media_final)}</td><td>{r.faltas_total}</td><td>{r.situacao_final}</td></tr>)}</tbody></table></div>}
      </section>
    </>}
  </ConsultaLayout>
}

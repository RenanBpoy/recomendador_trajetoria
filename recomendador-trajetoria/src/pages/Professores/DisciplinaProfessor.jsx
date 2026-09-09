import { taxa } from '../../utils/professores'
import { Link } from 'react-router-dom'

export default function DisciplinaProfessor({ disciplina }) {
  return (
    <article className="professor-discipline">
      <header><span>{disciplina.codigo}</span><h3>{disciplina.nome}</h3></header>
      <div className="professor-discipline__rate"><strong>{taxa(disciplina.taxa_aprovacao)}</strong><span>de aprovação{disciplina.resultados_avaliados > 0 && ` · ${disciplina.resultados_avaliados} resultados`}</span></div>
      {disciplina.taxa_aprovacao != null && <meter min="0" max="100" value={disciplina.taxa_aprovacao} aria-label={`Taxa de aprovação em ${disciplina.nome}`} />}
      <p>{disciplina.aprovados} aprovações · {disciplina.reprovados} reprovações</p>
      <details>
        <summary>Ver {disciplina.turmas.length} {disciplina.turmas.length === 1 ? 'turma' : 'turmas'}</summary>
        <ul>{disciplina.turmas.map((turma) => (
          <li key={turma.id}>
            <Link className="professor-discipline__class-link" to={`/diarios-classe/${turma.id}`} aria-label={`Abrir diário de ${disciplina.nome}, turma ${turma.codigo_turma}, ${turma.ano}/${turma.semestre}`}>
            <div><strong>{turma.ano}/{turma.semestre} · {turma.codigo_turma}</strong><span>{taxa(turma.taxa_aprovacao)}</span></div>
            <p>{turma.aprovados} aprovações · {turma.reprovados} reprovações</p>
            {turma.outros_resultados > 0 && <small>{turma.outros_resultados} outros resultados fora do cálculo</small>}
            {turma.compartilhada && <small>Turma compartilhada com outros docentes</small>}
            <span className="professor-discipline__diary-label">Abrir diário de classe ›</span>
            </Link>
          </li>
        ))}</ul>
      </details>
    </article>
  )
}

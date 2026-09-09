from uuid import UUID
from app.core.errors import ResourceNotFoundError
from app.domain.professores import ProfessoresRepository


def estatisticas(aprovados: int, reprovados: int, total: int) -> dict:
    avaliados = aprovados + reprovados
    return dict(aprovados=aprovados, reprovados=reprovados, outros_resultados=total-avaliados,
                resultados_avaliados=avaliados,
                taxa_aprovacao=round(aprovados / avaliados * 100, 1) if avaliados else None)


class ProfessoresService:
    def __init__(self, repository: ProfessoresRepository):
        self.repository = repository

    async def buscar(self, nome: str, limite: int, inicio: int):
        rows = await self.repository.buscar(nome.strip(), limite + 1, inicio)
        return dict(itens=rows[:limite], tem_mais=len(rows) > limite)

    async def perfil(self, professor_id: UUID):
        professor = await self.repository.obter(professor_id)
        if professor is None:
            raise ResourceNotFoundError('Professor', str(professor_id))
        turmas = await self.repository.turmas(professor_id)
        # Ofertas sem aprovação nem reprovação não possuem resultados úteis para
        # as estatísticas e, por isso, não devem aparecer no perfil do docente.
        turmas = [turma for turma in turmas if turma.aprovados + turma.reprovados > 0]
        disciplinas = {}
        for turma in turmas:
            item = disciplinas.setdefault(turma.disciplina_codigo, dict(codigo=turma.disciplina_codigo, nome=turma.disciplina, turmas=[]))
            item['turmas'].append(dict(id=turma.id, ano=turma.ano, semestre=turma.semestre,
                codigo_turma=turma.codigo_turma, compartilhada=turma.total_docentes > 1,
                **estatisticas(turma.aprovados, turma.reprovados, turma.total_matriculas)))
        for item in disciplinas.values():
            rows = item['turmas']
            item.update(estatisticas(sum(t['aprovados'] for t in rows), sum(t['reprovados'] for t in rows),
                sum(t['resultados_avaliados'] + t['outros_resultados'] for t in rows)))
        return dict(id=professor.id, nome=professor.nome, total_turmas=len(turmas),
            disciplinas=sorted(disciplinas.values(), key=lambda d: (d['nome'], d['codigo'])),
            **estatisticas(sum(t.aprovados for t in turmas), sum(t.reprovados for t in turmas), sum(t.total_matriculas for t in turmas)))

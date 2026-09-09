from uuid import UUID
from app.core.errors import ResourceNotFoundError
from app.domain.consultas import ConsultasAcademicasRepository
from app.domain.ports import AcademicDataProvider
from app.services.professores import estatisticas


class ConsultasAcademicasService:
    def __init__(self, repository: ConsultasAcademicasRepository, provider: AcademicDataProvider):
        self.repository = repository
        self.provider = provider

    async def buscar(self, busca: str, inicio: int, limite: int):
        items = await self.repository.disciplinas(busca.strip(), inicio, limite + 1)
        return dict(itens=items[:limite], tem_mais=len(items) > limite)

    async def disciplina(self, codigo: str):
        codigo = codigo.strip().upper()
        disciplina = await self.provider.get_discipline(codigo)
        if disciplina is None:
            raise ResourceNotFoundError('Disciplina', codigo)
        turmas = await self.repository.turmas(codigo)
        counts = await self.repository.resumo(codigo=codigo)
        return dict(codigo=disciplina.codigo, nome=disciplina.nome, turmas=turmas,
            cargas_horarias=sorted({t['carga_horaria'] for t in turmas}),
            **estatisticas(counts['aprovados'], counts['reprovados'], counts['total_registros']))

    async def diario(self, oferta_id: UUID, matricula: str, acesso_completo: bool):
        oferta = await self.provider.get_class_offering(oferta_id)
        if oferta is None or oferta.fonte_dados != 'DIARIO_CLASSE':
            raise ResourceNotFoundError('Diário de classe', str(oferta_id))
        counts = await self.repository.resumo(oferta_id=oferta_id)
        registros = await self.repository.matriculas(oferta_id, None if acesso_completo else matricula)
        return dict(oferta=oferta, acesso_completo=acesso_completo, registros=registros,
            **estatisticas(counts['aprovados'], counts['reprovados'], counts['total_registros']))

from uuid import UUID
from fastapi import APIRouter, Query, Request
from app.dependencies.auth import CurrentProfileDep
from app.dependencies.professores import ProfessoresServiceDep
from app.schemas.common import ApiResponse, ErrorResponse, response_meta
from app.schemas.professores import BuscaProfessoresOut, PerfilProfessorOut

router = APIRouter(prefix='/professores', tags=['Professores'])


def example(data):
    return {200: {'content': {'application/json': {'examples': {'exemplo': {'value': {'data': data, 'meta': {'request_id': 'exemplo-professores'}}}}}}},
            401: {'model': ErrorResponse}, 404: {'model': ErrorResponse}}


@router.get('', response_model=ApiResponse[BuscaProfessoresOut], summary='Pesquisar professores por nome',
    description='Busca paginada nos docentes cadastrados. Requer login. Não retorna dados de estudantes.',
    responses=example({'itens': [{'id': '00000000-0000-0000-0000-000000000001', 'nome': 'Professor de exemplo'}], 'tem_mais': False}))
async def buscar(request: Request, profile: CurrentProfileDep, service: ProfessoresServiceDep,
    nome: str = Query('', max_length=120), limite: int = Query(30, ge=1, le=100), inicio: int = Query(0, ge=0)):
    return ApiResponse(data=BuscaProfessoresOut.model_validate(await service.buscar(nome, limite, inicio)), meta=response_meta(request))


@router.get('/{professor_id}', response_model=ApiResponse[PerfilProfessorOut], summary='Consultar perfil e estatísticas de um professor',
    description='Somente ofertas vinculadas ao docente em oferta_docente. Taxa = aprovados / (aprovados + reprovados) × 100, incluindo reprovação por frequência. Demais situações não entram no denominador. Cada matrícula é uma tentativa; uma pessoa pode ter várias. Turmas com co-docência são sinalizadas. Taxas sem resultados são nulas. Não representa avaliação da qualidade docente.',
    responses=example({'id': '00000000-0000-0000-0000-000000000001', 'nome': 'Professor de exemplo', 'total_turmas': 0, 'disciplinas': [], 'aprovados': 0, 'reprovados': 0, 'outros_resultados': 0, 'resultados_avaliados': 0, 'taxa_aprovacao': None}))
async def perfil(professor_id: UUID, request: Request, profile: CurrentProfileDep, service: ProfessoresServiceDep):
    return ApiResponse(data=PerfilProfessorOut.model_validate(await service.perfil(professor_id)), meta=response_meta(request))

from uuid import UUID
from fastapi import APIRouter, Query, Request
from app.dependencies.auth import CurrentProfileDep
from app.dependencies.consultas import ConsultasServiceDep
from app.schemas.common import ApiResponse, response_meta
from app.schemas.consultas import BuscaDisciplinasOut, ConsultaDisciplinaOut, DiarioClasseOut
from app.api.v1.endpoints.professores import example

router = APIRouter(tags=['Consultas acadêmicas'])


@router.get('/consultas/disciplinas', response_model=ApiResponse[BuscaDisciplinasOut], summary='Pesquisar disciplinas por nome ou código',
    description='Catálogo pesquisável para estudantes autenticados, com paginação.', responses=example({'itens': [], 'tem_mais': False}))
async def buscar(request: Request, profile: CurrentProfileDep, service: ConsultasServiceDep,
    busca: str = Query('', max_length=120), inicio: int = Query(0, ge=0), limite: int = Query(30, ge=1, le=100)):
    return ApiResponse(data=BuscaDisciplinasOut.model_validate(await service.buscar(busca, inicio, limite)), meta=response_meta(request))


@router.get('/consultas/disciplinas/{codigo}', response_model=ApiResponse[ConsultaDisciplinaOut], summary='Consultar estatísticas e turmas de uma disciplina',
    description='Resultados de todas as turmas do código exato, sem misturar equivalências. Taxa de aprovação usa aprovações e reprovações, incluindo frequência; demais situações ficam fora. Uma matrícula é uma tentativa.',
    responses=example({'codigo': 'ELC1080', 'nome': 'Sistemas Operacionais A', 'cargas_horarias': [], 'turmas': [], 'aprovados': 0, 'reprovados': 0, 'outros_resultados': 0, 'resultados_avaliados': 0, 'taxa_aprovacao': None}))
async def disciplina(codigo: str, request: Request, profile: CurrentProfileDep, service: ConsultasServiceDep):
    return ApiResponse(data=ConsultaDisciplinaOut.model_validate(await service.disciplina(codigo)), meta=response_meta(request))


@router.get('/diarios-classe/{oferta_id}', response_model=ApiResponse[DiarioClasseOut], summary='Consultar um diário de classe',
    description='Consulta completa dos registros importados da turma, disponível para usuários autenticados. O responsável pelo projeto confirmou que os diários são públicos. Não retorna históricos enviados pelos usuários nem dados de contas.',
    responses=example({'acesso_completo': True, 'registros': [], 'aprovados': 0, 'reprovados': 0, 'outros_resultados': 0, 'resultados_avaliados': 0, 'taxa_aprovacao': None,
      'oferta': {'id': '00000000-0000-0000-0000-000000000001', 'curso_codigo': '314', 'curso_nome': 'Sistemas de Informação', 'disciplina_codigo': 'ELC1080', 'disciplina_nome': 'Sistemas Operacionais A', 'ano': 2026, 'semestre': 1, 'codigo_turma': 'SI', 'carga_horaria': 60, 'creditos': 4, 'situacao': 'Encerrada', 'docentes': [], 'fonte_dados': 'DIARIO_CLASSE', 'fonte_referencia': None, 'horarios': []}}))
async def diario(oferta_id: UUID, request: Request, profile: CurrentProfileDep, service: ConsultasServiceDep):
    result = await service.diario(oferta_id, profile.matricula, True)
    return ApiResponse(data=DiarioClasseOut.model_validate(result), meta=response_meta(request))

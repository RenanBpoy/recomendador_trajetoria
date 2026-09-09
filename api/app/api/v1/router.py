from fastapi import APIRouter
from app.api.v1.endpoints import professores
from app.api.v1.endpoints import consultas

from app.api.v1.endpoints import alunos, autenticacao, curriculos, cursos, disciplinas, historicos, ofertas, perfil, planos, primeiro_acesso, questionarios, recomendacoes, status

router = APIRouter()
router.include_router(professores.router)
router.include_router(consultas.router)
router.include_router(status.router)
router.include_router(autenticacao.router)
router.include_router(cursos.router)
router.include_router(curriculos.router)
router.include_router(disciplinas.router)
router.include_router(ofertas.router)
router.include_router(alunos.router)
router.include_router(historicos.router)
router.include_router(perfil.router)
router.include_router(primeiro_acesso.router)
router.include_router(planos.router)
router.include_router(questionarios.router)
router.include_router(recomendacoes.router)

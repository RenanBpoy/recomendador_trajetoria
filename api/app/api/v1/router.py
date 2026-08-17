from fastapi import APIRouter

from app.api.v1.endpoints import alunos, autenticacao, curriculos, cursos, disciplinas, ofertas, status

router = APIRouter()
router.include_router(status.router)
router.include_router(autenticacao.router)
router.include_router(cursos.router)
router.include_router(curriculos.router)
router.include_router(disciplinas.router)
router.include_router(ofertas.router)
router.include_router(alunos.router)

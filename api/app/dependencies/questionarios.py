from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import DatabaseSession
from app.repositories.questionarios import SqlAlchemyQuestionarioRepository
from app.services.questionarios import QuestionarioService


def get_questionnaire_service(session: DatabaseSession) -> QuestionarioService:
    return QuestionarioService(SqlAlchemyQuestionarioRepository(session))


QuestionarioServiceDep = Annotated[
    QuestionarioService, Depends(get_questionnaire_service)
]

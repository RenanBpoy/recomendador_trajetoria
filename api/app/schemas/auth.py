import re
from datetime import date
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SignupRequest(BaseModel):
    nome: str = Field(min_length=3, max_length=200)
    matricula: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=5, max_length=254)
    data_nascimento: date
    curso_codigo: str = Field(min_length=1, max_length=50)
    senha: str = Field(min_length=8, max_length=128, repr=False)
    confirmacao_senha: str = Field(min_length=8, max_length=128, repr=False)
    aceitou_termos: bool

    @field_validator("nome", "matricula", "curso_codigo")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("Informe um e-mail válido.")
        return normalized

    @field_validator("data_nascimento")
    @classmethod
    def reject_future_birthdate(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")
        return value

    @model_validator(mode="after")
    def validate_confirmation_and_terms(self) -> Self:
        if self.senha != self.confirmacao_senha:
            raise ValueError("A confirmação de senha não corresponde à senha.")
        if not self.aceitou_termos:
            raise ValueError("É necessário aceitar os termos para criar a conta.")
        return self


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    senha: str = Field(min_length=1, max_length=128, repr=False)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("Informe um e-mail válido.")
        return normalized


class AuthSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AuthUserOut(AuthSchema):
    id: UUID
    email: str


class AuthSessionOut(AuthSchema):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str


class UserProfileOut(AuthSchema):
    id: UUID
    matricula: str
    curso_codigo: str
    nome: str
    ppc_id: int | None = None
    data_nascimento: date | None = None
    avatar_url: str | None = None


class UpdatePersonalDataRequest(BaseModel):
    nome: str = Field(min_length=3, max_length=200)
    data_nascimento: date

    @field_validator("nome")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("data_nascimento")
    @classmethod
    def reject_future_birthdate(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")
        return value


class UpdateEmailRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("Informe um e-mail válido.")
        return normalized


class UpdatePasswordRequest(BaseModel):
    senha: str = Field(min_length=8, max_length=128, repr=False)
    confirmacao_senha: str = Field(min_length=8, max_length=128, repr=False)

    @model_validator(mode="after")
    def validate_confirmation(self) -> Self:
        if self.senha != self.confirmacao_senha:
            raise ValueError("A confirmação de senha não corresponde à senha.")
        return self


class EmailUpdateOut(BaseModel):
    email_solicitado: str
    confirmacao_necessaria: bool


class OperationMessageOut(BaseModel):
    mensagem: str


class SelectCurriculumRequest(BaseModel):
    ppc_id: int = Field(gt=0)


class SignupOut(AuthSchema):
    usuario: AuthUserOut
    sessao: AuthSessionOut | None
    confirmacao_email_necessaria: bool
    perfil: UserProfileOut | None = None


class LoginOut(AuthSchema):
    usuario: AuthUserOut
    sessao: AuthSessionOut
    perfil: UserProfileOut

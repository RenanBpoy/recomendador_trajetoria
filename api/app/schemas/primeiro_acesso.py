from pydantic import BaseModel, ConfigDict


class ResetPrimeiroAcessoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mensagem: str
    historicos_importados_removidos: int
    equivalencias_manuais_removidas: int
    questionarios_reiniciados: int
    itens_plano_removidos: int

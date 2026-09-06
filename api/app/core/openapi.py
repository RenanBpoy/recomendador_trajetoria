"""Configuração central da documentação OpenAPI/Swagger da API.

Os exemplos ficam aqui para que a documentação não dependa da implementação
atual do banco. Os endpoints continuam expondo os mesmos schemas mesmo quando
o ``AcademicDataProvider`` for substituído por outra fonte acadêmica.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


API_DESCRIPTION = """
API REST do **Recomendador de Trajetória Acadêmica**.

## Formato das respostas

As respostas de sucesso usam `data` e `meta`. O campo `meta.request_id` permite
relacionar uma resposta aos registros da API. As listas paginadas também
informam `limit` e `next_cursor`.

Os erros usam `error.code`, `error.message`, `error.details` e o mesmo bloco
`meta`.

## Fonte dos dados acadêmicos

Os endpoints não consultam diretamente o Supabase. O fluxo é:

`Endpoint → Service → AcademicDataProvider → fonte de dados`

Atualmente, o `CompositeAcademicDataProvider` combina o PostgreSQL do Supabase
com o histórico importado pelo estudante.

## Autenticação

Rotas com o ícone de cadeado exigem o token retornado pelo login. No Swagger,
clique em **Authorize** e informe somente o token JWT; a interface adicionará o
prefixo `Bearer` automaticamente.
"""


OPENAPI_TAGS = [
    {"name": "Infraestrutura", "description": "Disponibilidade e identificação da API."},
    {"name": "Autenticação", "description": "Cadastro e login por meio do Supabase Auth."},
    {"name": "Cursos", "description": "Cursos acadêmicos normalizados pelo AcademicDataProvider."},
    {"name": "PPCs", "description": "Versões de PPC e suas sequências curriculares aconselhadas."},
    {"name": "Disciplinas", "description": "Catálogo de disciplinas acadêmicas."},
    {"name": "Ofertas de turma", "description": "Turmas, docentes e encontros por período letivo."},
    {"name": "Alunos", "description": "Dados acadêmicos vinculados à matrícula do usuário autenticado."},
    {"name": "Históricos", "description": "Importação de PDF e equivalências de disciplinas."},
    {"name": "Perfil", "description": "Dados pessoais, PPC e foto do estudante autenticado."},
    {"name": "Plano semanal", "description": "Compromissos semanais usados para calcular disponibilidade."},
    {"name": "Questionários", "description": "Questionário pessoal e respostas usadas pela recomendação."},
    {"name": "Recomendações", "description": "Contexto curricular e recomendação acadêmica explicável."},
]


REQUEST_ID = "8d0b9de2-948e-4c48-bd86-8051b50bd3e4"


def api_response(data: Any) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": REQUEST_ID}}


def page_response(data: list[Any], *, next_cursor: str | None = None) -> dict[str, Any]:
    return {
        "data": data,
        "meta": {"request_id": REQUEST_ID, "limit": 50, "next_cursor": next_cursor},
    }


COURSE = {"codigo": "314", "nome": "Sistemas de Informação"}
CURRICULUM = {
    "id": 1,
    "curso_codigo": "314",
    "ano_versao": 2026,
    "nome": "PPC Sistemas de Informação 2026",
    "curriculo_corrente": True,
    "periodos_ideais": 8,
    "carga_horaria_total": 3200,
    "carga_horaria_extensao": 320,
    "fonte_referencia": "Projeto Pedagógico do Curso",
}
DISCIPLINE = {"codigo": "ELC1080", "nome": "Sistemas Operacionais A"}
SCHEDULE = {
    "id": 4501,
    "dia_semana": 2,
    "dia_nome": "Terça-feira",
    "hora_inicio": "08:30:00",
    "hora_fim": "10:30:00",
    "sala": "CT 07 - 336",
}
OFFERING_ID = "a3feebda-ae69-4c98-b820-95636530d3c2"
OFFERING = {
    "id": OFFERING_ID,
    "curso_codigo": "314",
    "curso_nome": "Sistemas de Informação",
    "disciplina_codigo": "ELC1080",
    "disciplina_nome": "Sistemas Operacionais A",
    "ano": 2026,
    "semestre": 2,
    "codigo_turma": "11",
    "carga_horaria": 60,
    "creditos": 4,
    "situacao": "ABERTA",
    "docentes": [
        {"id": "95ff721d-782d-403b-a653-a345c9321905", "nome": "Docente Exemplo"}
    ],
    "fonte_dados": "ENSALAMENTO_UFSM",
    "fonte_referencia": "ensalamento_2026-08-24.xlsx",
    "horarios": [SCHEDULE],
}
PROFILE = {
    "id": "a6130b39-a30f-48fd-965b-52bd81c17481",
    "matricula": "202320569",
    "curso_codigo": "314",
    "nome": "Estudante Exemplo",
    "ppc_id": 1,
    "data_nascimento": "2003-05-15",
    "avatar_url": None,
}
HISTORY_ITEM = {
    "matricula": "202320569",
    "disciplina_codigo": "ELC1080",
    "disciplina": "Sistemas Operacionais A",
    "professores": "Docente Exemplo",
    "ano": 2025,
    "semestre": 2,
    "codigo_turma": "11",
    "media_final": 8.5,
    "faltas_total": 2,
    "situacao_final": "APROVADO",
    "fonte": "DIARIO_CLASSE",
    "disciplina_codigo_origem": None,
    "disciplina_origem": None,
    "metodo_correspondencia": None,
    "confianca_correspondencia": None,
}
PLAN_ITEM = {
    "id": 31,
    "tipo_atividade": "ESTAGIO",
    "titulo": "Estágio",
    "dia_semana": 1,
    "hora_inicio": "13:30:00",
    "hora_fim": "17:30:00",
    "observacoes": "Atividade presencial",
}
QUESTIONNAIRE = {
    "id": 1,
    "codigo": "PERFIL_ACADEMICO",
    "versao": 1,
    "titulo": "Perfil acadêmico",
    "descricao": "Afirmações pessoais usadas como contexto da recomendação.",
    "escala_minima": 1,
    "escala_maxima": 10,
    "secoes": [
        {
            "id": 1,
            "codigo": "ROTINA",
            "ordem": 1,
            "titulo": "Rotina e contexto acadêmico",
            "descricao": "Disponibilidade e organização semanal.",
            "orientacao": "Responda de 1 a 10.",
            "perguntas": [
                {
                    "id": 1,
                    "codigo": "TEMPO_ESTUDO",
                    "ordem_global": 1,
                    "ordem_secao": 1,
                    "texto": "Consigo reservar tempo durante a semana para estudar fora das aulas.",
                    "peso_recomendacao": 0.18,
                    "resposta": 8,
                }
            ],
        }
    ],
    "preenchimento": {
        "id": "c5727d6e-2217-407d-a3a6-ce19381019e1",
        "status": "EM_ANDAMENTO",
        "total_perguntas": 8,
        "total_respondidas": 1,
        "atualizado_em": "2026-08-29T14:20:00Z",
        "concluido_em": None,
    },
}
IMPORT_RESULT = {
    "id": "d4d69102-3aa1-4a25-aa76-7b30bf8e95d0",
    "nome_arquivo": "historico-escolar.pdf",
    "criado_em": "2026-08-29T13:40:00Z",
    "curso_codigo_documento": "314",
    "ppc_ano_documento": 2026,
    "ppc_referencia_id": 1,
    "total_itens": 1,
    "identificados": 1,
    "requerem_confirmacao": 0,
    "nao_identificados": 0,
    "itens": [
        {
            "id": 804,
            "codigo_original": "ELC1080",
            "nome_original": "Sistemas Operacionais A",
            "carga_horaria": 60,
            "ano": 2025,
            "semestre": 2,
            "situacao": "APROVADO",
            "media": 8.5,
            "correspondencia_id": 410,
            "disciplina_codigo": "ELC1080",
            "disciplina_nome": "Sistemas Operacionais A",
            "metodo_correspondencia": "CODIGO",
            "confianca_correspondencia": 1.0,
            "status_correspondencia": "CONFIRMADA",
        }
    ],
}
MANUAL_EQUIVALENCE = {
    "id": 15,
    "ppc_id": 1,
    "ppc_componente_id": 88,
    "slot_ordem": 1,
    "historico_item_id": 804,
    "codigo_original": "ELC1080",
    "nome_original": "Sistemas Operacionais A",
    "carga_horaria": 60,
    "ano": 2025,
    "semestre": 2,
    "situacao": "APROVADO",
    "media": 8.5,
    "tipo_componente": "OBRIGATORIA",
    "nome_componente": "Sistemas Operacionais",
    "disciplina_codigo": "ELC1080",
}
CONTEXT = {
    "matricula": "202320569",
    "regra_matricula": "AAAA S: quatro primeiros dígitos representam o ano e o quinto o semestre de ingresso.",
    "prefixo_ingresso": "20232",
    "ano_ingresso": 2023,
    "semestre_ingresso": 2,
    "ano_alvo": 2026,
    "semestre_alvo": 2,
    "semestre_cronologico": 7,
    "semestre_curricular": 5,
    "regra_semestre_curricular": "Primeiro período do PPC com menos de 50% da carga obrigatória aprovada. Com 50% ou mais, o período é consolidado e as disciplinas restantes são tratadas como atrasadas, respeitando o limite do semestre cronológico.",
    "curso_codigo": "314",
    "ppc_id": 1,
    "ppc_ano": 2026,
    "ppc_nome": "PPC Sistemas de Informação 2026",
}
RECOMMENDATION = {
    "titulo": "Sugestão para 2026/2",
    "mensagem": "Foram selecionadas 4 disciplinas compatíveis com sua disponibilidade.",
    "contexto": CONTEXT,
    "carga_horaria_total": 240,
    "horas_semanais": 16.0,
    "limite_horas_semanais": 20.0,
    "indice_questionario": 0.72,
    "questionario_concluido": True,
    "plano_semanal_considerado": True,
    "desempenho": {
        "tentativas_recentes": 8,
        "aprovacoes_recentes": 7,
        "taxa_aprovacao_recente": 87.5,
        "disciplinas_dificeis_cursadas": 2,
        "disciplinas_dificeis_aprovadas": 2,
        "limite_disciplinas_alto_risco": 2,
    },
    "pesos_questionario": [
        {
            "codigo": "TEMPO_ESTUDO",
            "texto": "Consigo reservar tempo durante a semana para estudar fora das aulas.",
            "peso": 0.18,
            "resposta": 8,
            "contribuicao_normalizada": 0.14,
        }
    ],
    "disciplinas": [
        {
            "componente_id": 88,
            "disciplina_codigo": "ELC1080",
            "oferta_disciplina_codigo": "ELC1080",
            "equivalencia_utilizada": False,
            "disciplina_nome": "Sistemas Operacionais A",
            "semestre_recomendado": 7,
            "atrasada": False,
            "adiantada": False,
            "oferta_turma_id": OFFERING_ID,
            "codigo_turma": "11",
            "carga_horaria": 60,
            "horas_semanais": 4.0,
            "taxa_reprovacao": 18.2,
            "amostra_taxa_reprovacao": 55,
            "nivel_risco": "baixo",
            "pontuacao": 91.4,
            "justificativa": "Esta disciplina acompanha o semestre curricular identificado pelo seu avanço na grade. Seu bom desempenho recente e a carga compatível favorecem sua inclusão neste semestre.",
            "motivos": ["Disciplina prevista para o semestre curricular atual."],
            "alertas": [],
            "horarios": [SCHEDULE],
            "dedicacao_extraclasse": {
                "nivel": "elevada",
                "titulo": "Tempo de dedicação elevado",
                "descricao": "Os alunos estimam mais de 3h de dedicação semanal.",
                "total_respostas": 6,
            },
        }
    ],
    "nao_selecionadas": [],
    "criterios": ["Priorizar o semestre atual e as pendências."],
    "alertas": [],
}


ENDPOINT_DESCRIPTIONS: dict[str, str] = {
    "GET /api/v1/status": "Confirma que o processo da API está respondendo. Não testa profundamente a disponibilidade do banco.",
    "POST /api/v1/autenticacao/cadastro": "Cria a identidade no Supabase Auth e o perfil acadêmico associado à matrícula e ao curso.",
    "POST /api/v1/autenticacao/login": "Valida e-mail e senha no Supabase Auth e devolve a sessão e o perfil acadêmico.",
    "GET /api/v1/cursos": "Lista cursos usando paginação por cursor através do contrato `AcademicDataProvider`.",
    "GET /api/v1/cursos/{codigo}": "Consulta um curso pelo código oficial, independentemente da fonte acadêmica ativa.",
    "GET /api/v1/cursos/{codigo}/ppcs": "Lista todas as versões de PPC cadastradas para o curso informado.",
    "GET /api/v1/ppcs/{ppc_id}": "Consulta os metadados de uma versão específica do projeto pedagógico.",
    "GET /api/v1/ppcs/{ppc_id}/componentes": "Devolve a sequência aconselhada, incluindo semestre, ordem, tipo e carga horária de cada componente.",
    "GET /api/v1/disciplinas": "Lista o catálogo normalizado de disciplinas com paginação por cursor.",
    "GET /api/v1/disciplinas/{codigo}": "Consulta uma disciplina pelo código acadêmico oficial.",
    "GET /api/v1/ofertas-turma": "Lista ofertas com docentes e todos os encontros cadastrados. Os filtros podem ser combinados.",
    "GET /api/v1/ofertas-turma/{oferta_id}": "Consulta uma oferta de turma e seus horários pelo identificador UUID.",
    "GET /api/v1/ofertas-turma/{oferta_id}/horarios": "Devolve somente os encontros de uma oferta, preservando vários dias para a mesma turma.",
    "GET /api/v1/periodos-letivos": "Lista pares de ano e semestre existentes nas ofertas de turma.",
    "GET /api/v1/alunos/{matricula}/historico": "Combina o histórico dos diários com o histórico importado. A matrícula deve pertencer ao usuário autenticado.",
    "GET /api/v1/alunos/{matricula}/disciplinas-nao-aprovadas": "Lista ofertas de disciplinas ainda não aprovadas que possuem ao menos um encontro sobreposto ao dia e intervalo informados. A busca usa todas as ofertas do período, não apenas as obrigatórias do PPC.",
    "POST /api/v1/historicos/importacoes": "Lê um histórico UFSM em PDF, normaliza as disciplinas e cria sugestões de correspondência. Envie `multipart/form-data` no campo `arquivo`.",
    "GET /api/v1/historicos/importacoes/atual": "Consulta a importação ativa mais recente do usuário, incluindo correspondências e itens não identificados.",
    "PATCH /api/v1/historicos/correspondencias/{correspondencia_id}": "Confirma ou rejeita uma correspondência automática sugerida durante a importação.",
    "GET /api/v1/historicos/equivalencias-manuais": "Lista as equivalências que o próprio estudante salvou para seu PPC.",
    "GET /api/v1/historicos/componentes/{componente_id}/candidatos-equivalencia": "Lista itens aprovados e ainda não mapeados que podem preencher o componente informado.",
    "PUT /api/v1/historicos/componentes/{componente_id}/vagas/{vaga_ordem}/equivalencia": "Associa manualmente um item do histórico a uma vaga do componente curricular.",
    "DELETE /api/v1/historicos/componentes/{componente_id}/vagas/{vaga_ordem}/equivalencia": "Remove a equivalência manual da vaga. Em caso de sucesso não há corpo de resposta.",
    "GET /api/v1/perfil": "Consulta o perfil autenticado e gera uma URL temporária para o avatar, quando houver.",
    "PUT /api/v1/perfil/ppc": "Valida e salva o PPC que será usado pela grade, progresso e recomendação.",
    "PATCH /api/v1/perfil/dados-pessoais": "Atualiza nome e data de nascimento do perfil acadêmico.",
    "PUT /api/v1/perfil/email": "Solicita a alteração do e-mail no Supabase Auth. A confirmação pode ser exigida pelo projeto.",
    "PUT /api/v1/perfil/senha": "Substitui a senha do usuário autenticado no Supabase Auth.",
    "POST /api/v1/perfil/avatar": "Envia JPG, PNG ou WebP de até 5 MB ao bucket privado de avatares.",
    "DELETE /api/v1/perfil/avatar": "Remove a imagem do Storage e limpa sua referência no perfil.",
    "GET /api/v1/plano-semanal": "Consulta os compromissos persistidos usados para calcular os horários livres.",
    "PUT /api/v1/plano-semanal": "Substitui integralmente o plano semanal. Envie a lista completa que deve permanecer salva.",
    "GET /api/v1/questionarios/atual": "Consulta a versão ativa do questionário e incorpora as respostas já salvas pelo usuário.",
    "PUT /api/v1/questionarios/atual/respostas/{pergunta_id}": "Salva uma resposta de 1 a 10 e devolve o questionário atualizado.",
    "POST /api/v1/questionarios/atual/concluir": "Marca o questionário como concluído após validar que todas as perguntas foram respondidas.",
    "GET /api/v1/recomendacoes/contexto": "Usa a matrícula para obter o semestre cronológico e o avanço nas obrigatórias do PPC para calcular o semestre curricular.",
    "GET /api/v1/recomendacoes/atual": "Gera uma recomendação explicável combinando PPC, histórico, ofertas, plano semanal, questionário e estatísticas de reprovação.",
}


RESPONSE_EXAMPLES: dict[str, Any] = {
    "GET /api/v1/status": api_response({"status": "ok", "service": "API do Recomendador de Trajetória"}),
    "POST /api/v1/autenticacao/cadastro": api_response(
        {
            "usuario": {"id": PROFILE["id"], "email": "estudante@example.com"},
            "sessao": None,
            "confirmacao_email_necessaria": True,
            "perfil": PROFILE,
        }
    ),
    "POST /api/v1/autenticacao/login": api_response(
        {
            "usuario": {"id": PROFILE["id"], "email": "estudante@example.com"},
            "sessao": {
                "access_token": "eyJhbGciOiJIUzI1NiJ9.token-de-exemplo",
                "refresh_token": "refresh-token-de-exemplo",
                "expires_in": 3600,
                "token_type": "bearer",
            },
            "perfil": PROFILE,
        }
    ),
    "GET /api/v1/cursos": page_response([COURSE], next_cursor="314"),
    "GET /api/v1/cursos/{codigo}": api_response(COURSE),
    "GET /api/v1/cursos/{codigo}/ppcs": api_response([CURRICULUM]),
    "GET /api/v1/ppcs/{ppc_id}": api_response(CURRICULUM),
    "GET /api/v1/ppcs/{ppc_id}/componentes": api_response(
        [
            {
                "id": 88,
                "ppc_id": 1,
                "disciplina_codigo": "ELC1080",
                "semestre_recomendado": 7,
                "ordem_semestre": 2,
                "tipo_componente": "OBRIGATORIA",
                "nome_no_ppc": "Sistemas Operacionais A",
                "disciplina_nome": "Sistemas Operacionais A",
                "carga_horaria": 60,
            }
        ]
    ),
    "GET /api/v1/disciplinas": page_response([DISCIPLINE], next_cursor="ELC1080"),
    "GET /api/v1/disciplinas/{codigo}": api_response(DISCIPLINE),
    "GET /api/v1/ofertas-turma": page_response([OFFERING], next_cursor=OFFERING_ID),
    "GET /api/v1/ofertas-turma/{oferta_id}": api_response(OFFERING),
    "GET /api/v1/ofertas-turma/{oferta_id}/horarios": api_response([SCHEDULE]),
    "GET /api/v1/periodos-letivos": api_response([{"ano": 2026, "semestre": 2}]),
    "GET /api/v1/alunos/{matricula}/historico": api_response([HISTORY_ITEM]),
    "GET /api/v1/alunos/{matricula}/disciplinas-nao-aprovadas": api_response([OFFERING]),
    "POST /api/v1/historicos/importacoes": api_response(IMPORT_RESULT),
    "GET /api/v1/historicos/importacoes/atual": api_response(IMPORT_RESULT),
    "PATCH /api/v1/historicos/correspondencias/{correspondencia_id}": api_response(IMPORT_RESULT),
    "GET /api/v1/historicos/equivalencias-manuais": api_response([MANUAL_EQUIVALENCE]),
    "GET /api/v1/historicos/componentes/{componente_id}/candidatos-equivalencia": api_response(
        [
            {
                "id": 804,
                "codigo_original": "ELC1080",
                "nome_original": "Sistemas Operacionais A",
                "carga_horaria": 60,
                "ano": 2025,
                "semestre": 2,
                "situacao": "APROVADO",
                "media": 8.5,
                "selecionavel": True,
                "motivo_indisponibilidade": None,
                "similaridade_nome": 0.94,
                "em_uso": False,
                "componente_em_uso_id": None,
                "slot_em_uso": None,
            }
        ]
    ),
    "PUT /api/v1/historicos/componentes/{componente_id}/vagas/{vaga_ordem}/equivalencia": api_response(MANUAL_EQUIVALENCE),
    "GET /api/v1/perfil": api_response(PROFILE),
    "PUT /api/v1/perfil/ppc": api_response(PROFILE),
    "PATCH /api/v1/perfil/dados-pessoais": api_response(PROFILE),
    "PUT /api/v1/perfil/email": api_response(
        {"email_solicitado": "novo-email@example.com", "confirmacao_necessaria": True}
    ),
    "PUT /api/v1/perfil/senha": api_response({"mensagem": "Senha atualizada com sucesso."}),
    "POST /api/v1/perfil/avatar": api_response({**PROFILE, "avatar_url": "https://example.supabase.co/storage/v1/object/sign/avatares/avatar.webp"}),
    "DELETE /api/v1/perfil/avatar": api_response(PROFILE),
    "GET /api/v1/plano-semanal": api_response([PLAN_ITEM]),
    "PUT /api/v1/plano-semanal": api_response([PLAN_ITEM]),
    "GET /api/v1/questionarios/atual": api_response(QUESTIONNAIRE),
    "PUT /api/v1/questionarios/atual/respostas/{pergunta_id}": api_response(QUESTIONNAIRE),
    "POST /api/v1/questionarios/atual/concluir": api_response(
        {
            **QUESTIONNAIRE,
            "preenchimento": {
                **QUESTIONNAIRE["preenchimento"],
                "status": "CONCLUIDO",
                "total_respondidas": 8,
                "concluido_em": "2026-08-29T14:30:00Z",
            },
        }
    ),
    "GET /api/v1/recomendacoes/contexto": api_response(CONTEXT),
    "GET /api/v1/recomendacoes/atual": api_response(RECOMMENDATION),
}


REQUEST_EXAMPLES: dict[str, Any] = {
    "POST /api/v1/autenticacao/cadastro": {
        "nome": "Estudante Exemplo",
        "matricula": "202320569",
        "email": "estudante@example.com",
        "data_nascimento": "2003-05-15",
        "curso_codigo": "314",
        "senha": "senha-segura-123",
        "confirmacao_senha": "senha-segura-123",
        "aceitou_termos": True,
    },
    "POST /api/v1/autenticacao/login": {
        "email": "estudante@example.com",
        "senha": "senha-segura-123",
    },
    "PATCH /api/v1/historicos/correspondencias/{correspondencia_id}": {"acao": "confirmar"},
    "PUT /api/v1/historicos/componentes/{componente_id}/vagas/{vaga_ordem}/equivalencia": {"historico_item_id": 804},
    "PUT /api/v1/perfil/ppc": {"ppc_id": 1},
    "PATCH /api/v1/perfil/dados-pessoais": {
        "nome": "Estudante Exemplo",
        "data_nascimento": "2003-05-15",
    },
    "PUT /api/v1/perfil/email": {"email": "novo-email@example.com"},
    "PUT /api/v1/perfil/senha": {
        "senha": "nova-senha-segura-123",
        "confirmacao_senha": "nova-senha-segura-123",
    },
    "PUT /api/v1/plano-semanal": {
        "itens": [
            {
                "tipo_atividade": "ESTAGIO",
                "titulo": "Estágio",
                "dia_semana": 1,
                "hora_inicio": "13:30:00",
                "hora_fim": "17:30:00",
                "observacoes": "Atividade presencial",
            }
        ]
    },
    "PUT /api/v1/questionarios/atual/respostas/{pergunta_id}": {"valor": 8},
}


PARAMETER_EXAMPLES: dict[str, tuple[str, Any]] = {
    "codigo": ("Código oficial do recurso acadêmico.", "314"),
    "ppc_id": ("Identificador interno da versão do PPC.", 1),
    "oferta_id": ("UUID da oferta de turma.", OFFERING_ID),
    "matricula": ("Matrícula do estudante autenticado.", "202320569"),
    "correspondencia_id": ("Identificador da correspondência sugerida.", 410),
    "componente_id": ("Identificador do componente curricular no PPC.", 88),
    "vaga_ordem": ("Posição da vaga dentro do componente, iniciando em 1.", 1),
    "pergunta_id": ("Identificador da pergunta ativa.", 1),
    "limit": ("Quantidade máxima de registros devolvidos.", 50),
    "cursor": ("Cursor recebido na página anterior.", None),
    "curso_codigo": ("Filtra pelo código oficial do curso.", "314"),
    "disciplina_codigo": ("Filtra pelo código oficial da disciplina.", "ELC1080"),
    "ano": ("Ano do período acadêmico. Na recomendação, sobrescreve o ano atual.", 2026),
    "semestre": ("Semestre acadêmico, com valor 1 ou 2.", 2),
    "dia_semana": ("Dia da semana, de 1 (segunda) a 5 (sexta).", 2),
    "hora_inicio": ("Início do intervalo selecionado no plano.", "08:00:00"),
    "hora_fim": ("Fim do intervalo selecionado no plano.", "10:00:00"),
}


ERROR_EXAMPLES: dict[str, dict[str, Any]] = {
    "400": {"code": "application_error", "message": "Não foi possível executar a operação.", "details": None},
    "401": {"code": "authentication_failed", "message": "É necessário entrar na conta para acessar este recurso.", "details": None},
    "403": {"code": "historico_nao_autorizado", "message": "O histórico solicitado não pertence ao usuário logado.", "details": None},
    "404": {"code": "resource_not_found", "message": "Recurso não encontrado.", "details": {"identifier": "exemplo"}},
    "409": {"code": "resource_conflict", "message": "O recurso informado já está em uso.", "details": None},
    "422": {"code": "validation_error", "message": "Parâmetros inválidos.", "details": []},
    "429": {"code": "rate_limit_exceeded", "message": "Muitas tentativas. Tente novamente mais tarde.", "details": None},
    "500": {"code": "internal_error", "message": "Ocorreu um erro interno inesperado.", "details": None},
    "503": {"code": "data_source_unavailable", "message": "A fonte de dados acadêmicos está indisponível.", "details": None},
}


def _add_example(content: dict[str, Any], value: Any, summary: str) -> None:
    media_type = content.setdefault("application/json", {})
    media_type["examples"] = {"exemplo": {"summary": summary, "value": value}}


def _document_operation(path: str, method: str, operation: dict[str, Any]) -> None:
    key = f"{method.upper()} {path}"
    operation["description"] = ENDPOINT_DESCRIPTIONS.get(
        key,
        operation.get("summary", "Executa a operação documentada."),
    )

    response_example = RESPONSE_EXAMPLES.get(key)
    if response_example is not None:
        success_codes = sorted(
            code for code in operation.get("responses", {}) if code.startswith("2")
        )
        if success_codes:
            response = operation["responses"][success_codes[0]]
            _add_example(
                response.setdefault("content", {}),
                response_example,
                "Resposta de sucesso",
            )

    request_example = REQUEST_EXAMPLES.get(key)
    if request_example is not None:
        request_body = operation.get("requestBody", {})
        _add_example(
            request_body.setdefault("content", {}),
            request_example,
            "Corpo da requisição",
        )

    for parameter in operation.get("parameters", []):
        documentation = PARAMETER_EXAMPLES.get(parameter.get("name", ""))
        if documentation is None:
            continue
        description, example = documentation
        parameter.setdefault("description", description)
        if example is not None:
            parameter.setdefault("example", example)

    for status_code, response in operation.get("responses", {}).items():
        error = ERROR_EXAMPLES.get(status_code)
        if error is None:
            continue
        _add_example(
            response.setdefault("content", {}),
            {"error": error, "meta": {"request_id": REQUEST_ID}},
            f"Erro HTTP {status_code}",
        )


def configure_openapi(app: FastAPI) -> None:
    """Instala a geração enriquecida do OpenAPI usado pelo Swagger e ReDoc."""

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            summary=app.summary,
            description=app.description,
            routes=app.routes,
            tags=OPENAPI_TAGS,
            servers=[{"url": "/", "description": "Servidor em que a documentação está aberta"}],
        )
        schema["info"]["x-architecture"] = {
            "flow": "Endpoint -> Service -> AcademicDataProvider -> fonte de dados",
            "currentProvider": "CompositeAcademicDataProvider",
            "primarySource": "PostgresAcademicDataProvider (PostgreSQL/Supabase)",
            "additionalSource": "Históricos acadêmicos importados pelo estudante",
        }

        for path, path_item in schema.get("paths", {}).items():
            for method in ("get", "post", "put", "patch", "delete"):
                operation = path_item.get(method)
                if operation is not None:
                    _document_operation(path, method, operation)

        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi

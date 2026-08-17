# API do Recomendador de Trajetória

API REST desenvolvida com FastAPI para fornecer cursos, PPCs, disciplinas, ofertas de turma, histórico escolar e autenticação ao aplicativo Recomendador de Trajetória.

## Tecnologias

- Python 3.12+
- FastAPI
- SQLAlchemy assíncrono
- PostgreSQL/Supabase

## Configuração

Na pasta `api`, crie e ative o ambiente virtual e instale as dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
Copy-Item .env.example .env
```

Preencha o arquivo `.env` com a conexão do banco e as configurações públicas do Supabase utilizadas pela autenticação.

## Execução

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A API ficará disponível em `http://localhost:8000`. A documentação interativa pode ser consultada em `http://localhost:8000/docs`.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest
```

As pastas principais seguem a arquitetura em camadas: `api`, `services`, `providers`, `repositories`, `models`, `schemas`, `domain`, `dependencies` e `core`.

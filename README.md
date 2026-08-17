# Recomendador de Trajetória Acadêmica


## Estrutura do projeto

```text
recomendador_trajetoria/
├── api/                       API REST em FastAPI
├── recomendador-trajetoria/  Aplicação web em React
```

## Tecnologias principais

- React e Vite no frontend;
- FastAPI e Python na API;
- SQLAlchemy para acesso aos dados;
- PostgreSQL hospedado no Supabase;
- Supabase Auth para cadastro e login.

## Funcionalidades

- cadastro e login de estudantes;
- identificação do curso associado ao usuário;
- seleção da versão do PPC;
- exibição da sequência curricular recomendada;
- comparação da grade com o histórico escolar;
- consulta de cursos, disciplinas, PPCs e ofertas de turma pela API.

## Executando a API

Requer Python 3.12 ou superior. No diretório `api`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

O arquivo `api/.env` deve conter a conexão com o PostgreSQL e as configurações públicas do Supabase usadas pela autenticação.

A API fica disponível em `http://localhost:8000` e sua documentação interativa em `http://localhost:8000/docs`.

## Executando o frontend

Com a API em execução, abra o diretório `recomendador-trajetoria`:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Por padrão, o frontend utiliza:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

O endereço padrão do Vite é `http://localhost:5173`.

Mais informações estão no [README do frontend](recomendador-trajetoria/README.md).

## Organização da API

A API utiliza arquitetura em camadas. Os endpoints chamam os services, que acessam o contrato `AcademicDataProvider`. A implementação atual, `PostgresAcademicDataProvider`, usa repositories e SQLAlchemy para consultar o PostgreSQL. Essa separação permite adicionar outra fonte acadêmica no futuro sem alterar os endpoints.


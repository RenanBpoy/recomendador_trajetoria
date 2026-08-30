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
- Supabase Storage privado para fotos de perfil.

## Funcionalidades

- cadastro e login de estudantes;
- perfil funcional com edição de nome, nascimento, e-mail, senha, PPC e foto;
- identificação do curso associado ao usuário;
- seleção da versão do PPC;
- exibição da sequência curricular recomendada;
- comparação da grade com os diários de classe e com o histórico escolar enviado em PDF;
- reconhecimento de disciplinas equivalentes por código ou nome semelhante;
- divisão dos blocos de DCG em vagas de 60 horas e escolha manual de equivalências não detectadas;
- plano semanal interativo para incluir disciplinas, estágio e outras atividades, com edição e persistência por usuário;
- questionário acadêmico versionado com 8 afirmações, salvamento automático e retomada do progresso;
- consulta de cursos, disciplinas, PPCs e ofertas de turma pela API;
- horários oficiais de SI e CC para `2026/2`, com vários encontros por turma e salas;
- recomendação inicial explicável, combinando PPC, pendências, ofertas, plano semanal, desempenho, questionário e reprovação histórica;
- cache de dados por sessão no frontend, com invalidação após alterações acadêmicas.

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

A API fica disponível em `http://localhost:8000`.

### Documentação da API

Com a API em execução, estão disponíveis três formatos de documentação:

- Swagger interativo: `http://localhost:8000/docs`;
- ReDoc para leitura: `http://localhost:8000/redoc`;
- esquema OpenAPI em JSON: `http://localhost:8000/openapi.json`.

O Swagger apresenta descrições e exemplos de requisição e resposta para todos os endpoints. Nas rotas autenticadas, execute primeiro `POST /api/v1/autenticacao/login`, copie o valor de `data.sessao.access_token`, clique em **Authorize** e cole somente o token. A própria interface acrescenta `Bearer` ao cabeçalho.

A introdução da documentação também registra o fluxo desacoplado `Endpoint → Service → AcademicDataProvider → fonte de dados`. Os exemplos representam o contrato estável entregue ao frontend e continuam válidos se a fonte acadêmica atual for substituída.

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

## Organização da API

A API utiliza arquitetura em camadas. Os endpoints chamam os services, que acessam o contrato `AcademicDataProvider`. A implementação atual combina o `PostgresAcademicDataProvider`, responsável pelo banco acadêmico, com a fonte de históricos importados. O `PdfUfsmHistoricoProvider` adapta o documento da UFSM para o formato interno da aplicação. Essa separação permite adicionar outra fonte acadêmica no futuro sem alterar os endpoints.

O PPC escolhido pelo estudante fica salvo no perfil e é usado pela Home e pela Grade. O PDF original, CPF e documento de identidade não são armazenados; a importação guarda somente os dados acadêmicos necessários e o hash do arquivo.

O questionário é carregado pela API em `GET /api/v1/questionarios/atual`. Respostas de 1 a 10 são salvas individualmente e vinculadas ao usuário e à versão respondida. Cada uma das oito perguntas possui um peso explícito usado para ajustar o limite de carga da recomendação.

A recomendação é calculada em `GET /api/v1/recomendacoes/atual`. O contexto acadêmico e o semestre derivado da matrícula podem ser consultados separadamente em `GET /api/v1/recomendacoes/contexto`. A regra considera os quatro primeiros dígitos como ano de ingresso e o quinto como semestre de ingresso.

As ofertas podem ser filtradas por curso, disciplina, ano e semestre em `GET /api/v1/ofertas-turma`. Cada oferta devolve seus encontros em `horarios`; também é possível consultar somente os horários de uma oferta em `GET /api/v1/ofertas-turma/{oferta_id}/horarios`.

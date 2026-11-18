# Login UFSM (homologação)

1. Aplique `SQL/134_autenticacao_ufsm.sql` uma única vez no banco usado pelo backend.
2. Conecte a máquina que executa a API à VPN da UFSM.
3. No arquivo `api/.env`, defina `UFSM_AUTH_ENABLED=true`,
   `UFSM_CLIENT_ID=ext-trajetoria-academica` e `UFSM_CLIENT_SECRET` com o
   segredo atual enviado pela DTI. Reinicie o backend. A URL de retorno
   padrão é `http://localhost:5173/auth/callback` (`UFSM_REDIRECT_URI`)
   e deve ser idêntica à cadastrada pela DTI. Não use prefixo `VITE_`
   para segredos.
4. Abra `http://localhost:5173/login` (use `localhost`, não `127.0.0.1`) e
   clique em **Entrar pela UFSM**. Informe suas credenciais e confirme os
   escopos, se solicitado, somente no portal oficial.

`POST /api/v1/autenticacao/ufsm/iniciar` devolve o endereço do portal e um
identificador de tentativa, mantido na aba e válido por dez minutos.
O portal redireciona a aba para `/auth/callback?code=...`. Essa página
remove o código da URL e o envia, com a tentativa, para
`POST /api/v1/autenticacao/ufsm/callback`. O backend consome a tentativa
uma única vez, troca o código por token incluindo `redirectUri` e consulta
os vínculos regulares. Como o portal ainda não devolve `state`, o app pede
confirmação explícita da conta após o retorno, antes de abrir a sessão.
Se houver mais de um vínculo regular, o estudante escolhe qual acessar;
se houver apenas um, ele já vem selecionado. A sessão local só é emitida
em `POST /api/v1/autenticacao/ufsm/confirmar`, com uma confirmação de uso
único que expira em até cinco minutos. A UFSM recebe o segredo apenas
do backend; o aplicativo não recebe a senha institucional.
O logout revoga a sessão do aplicativo. Os cookies da UFSM pertencem ao
portal e o logout oficial não aceita requisições vindas da origem do app.
Após sair do Salomão ou clicar em **Trocar de conta** na tela de
confirmação, abra o portal oficial pelo botão indicado, escolha **Sair**
se a conta estiver aberta e depois volte ao app para continuar. O link
abre o portal sem `clientId` para não autorizar automaticamente o app.

O identificador `usuario.ufsm_id_pessoa` aponta para um novo perfil
local; as associações do cronograma e questionário continuam usando
`usuario.id`. Perfis Supabase existentes não são reutilizados nem
apagados. A configuração padrão permanece desabilitada.

O app carrega apenas o vínculo confirmado. A grade usa o `ppcId`
desse vínculo e consulta componentes, histórico, aproveitamentos e
equivalências oficiais. O resultado normalizado está na sessão privada
(`SQL/135_grade_ufsm.sql`); para atualizar, entre novamente.
O Plano e a recomendação usam o semestre da data atual no fuso da UFSM
(`America/Sao_Paulo`): de janeiro a junho é o semestre 1; de julho a dezembro,
o semestre 2. Ofertas publicadas para períodos futuros não mudam o
período padrão. Na API da recomendação ainda é possível informar `ano` e
`semestre` explicitamente.
O Plano consulta ofertas da DTI apenas para o curso e período necessários.
O modal lista os demais cursos pelo catálogo de nomes e códigos, sem
consultar ofertas. Ao expandir um curso, busca só as turmas desse curso
que coincidem com o intervalo selecionado. O cache do backend
reaproveita as ofertas de cada curso/período por até 30 minutos ao trocar
de horário. Consultas novas são sequenciais, com pelo menos 0,8 s entre
os inícios. Se a UFSM responder 429, o backend pausa chamadas de catálogo
até o prazo indicado em Retry-After (ou por 60 segundos se não houver
indicação) e retoma com o intervalo conservador de 1,25 s.
Para essas consultas o token institucional fica somente em memória no
backend de homologação (um processo); após reiniciar, entre novamente.
A recomendação reutiliza o mesmo motor com o PPC, o histórico, as
equivalências oficiais, as ofertas e as estatísticas da DTI. Os dados do
plano, do questionário e da pesquisa de dedicação extraclasse continuam
locais. Regras de equivalência com várias disciplinas só reconhecem uma
conclusão quando o grupo inteiro está cumprido; não são tratadas como
substituições individuais de oferta.

As estatísticas coletivas são reaproveitadas em memória por até seis horas.
A exclusão das tentativas do próprio estudante é calculada a cada análise,
sem colocar o histórico no cache. Candidatas sem oferta ou equivalente com
horário não precisam de uma consulta de risco para justificar a exclusão.
Os códigos necessários para calcular o desempenho continuam sendo consultados.

Se a DTI responder 404 apenas para a estatística de um código do
histórico (por exemplo, AEX00000), o código fica sem estatística e
não interrompe a análise. Isso não é interpretado como 0% de reprovação.

A API exige um curso ofertante por consulta. Além do curso do vínculo, o
motor consulta cursos indicados no catálogo local, nas ofertas já
consultadas no Plano e em `UFSM_RECOMMENDATION_EXTRA_COURSES` (307, 312 e
314 por padrão). O catálogo local só indica onde procurar; toda oferta
recomendada precisa ser confirmada pela DTI. Não é uma busca exaustiva
de todos os cursos da UFSM.
Avatar, alterações de conta e exclusão legada não são aplicáveis ao
perfil institucional nesta versão. A sessão expira junto ao token de
origem, sem renovação automática.

Para produção, confirme com a DTI a conectividade do backend e cadastre
a URL HTTPS de retorno do ambiente. A URL configurada na API precisa
ser idêntica à cadastrada na DTI. Em homologação, execute o backend com
um único processo: tentativas de login e tokens acadêmicos estão em
memória.

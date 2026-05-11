# API Quickstart

## Base

- entrypoint: `app.py`
- app interna: `source/app.py`
- prefixo principal: `/api/v1`
- healthcheck: `GET /api/v1/health`
- readiness de banco: `GET /api/v1/ready`
- `ready` agora tambem devolve diagnostico de configuracao do banco principal
- catalogo de rotas: `GET /api/v1/routes`
- convencoes da API: `GET /api/v1/conventions`
- plano de smoke test: `GET /api/v1/smoke-plan`
- checklist de seguranca: `GET /api/v1/security-check`
- manifesto de ambiente: `GET /api/v1/environment`
- `environment` agora tambem expone validacao da configuracao de banco carregada no runtime
- resumo da API: `GET /api/v1/about`
- referencia de payloads: `GET /api/v1/payloads`
- exemplos de body: `GET /api/v1/examples`
- referencia de query params: `GET /api/v1/queries`
- exemplos de resposta: `GET /api/v1/responses`
- catalogo modular: `GET /api/v1/catalog`
- catalogo resolvido por token: `GET /api/v1/catalog/<token_id>`
- sessao autenticada: `GET /api/v1/session/<token_id>`
- capabilities da sessao: `GET /api/v1/capabilities/<token_id>`
- feature map da sessao: `GET /api/v1/feature-map/<token_id>`
- acoes contextuais por registro: `GET /api/v1/context-actions/<entity>/<record_id>/<token_id>`
- contexto de tela: `GET /api/v1/screen-context/<token_id>`
- contexto de tela por registro: `GET /api/v1/screen-context/<entity>/<record_id>/<token_id>`

## Resposta padrao

- a API usa `NXResult`
- exemplo:

```json
{
  "nx_result": true,
  "status": true,
  "code": -1,
  "info": false,
  "warning": false,
  "error": false,
  "message": "Operacao realizada com sucesso",
  "error_msg": "",
  "data": {}
}
```

## Autenticacao

### Master

- `POST /api/v1/auth/master/login/`
- body:

```json
{
  "login": "admin",
  "password": "123456"
}
```

### Tenant

- `POST /api/v1/auth/tenant/login/`
- header obrigatorio: `X-Account-Code`
- body:

```json
{
  "email": "admin@empresa.com",
  "password": "123456"
}
```

## Padrao de acesso autenticado

- a maior parte da API autenticada usa `token_id` no path
- exemplo:

```text
/api/v1/projects/<token_id>
```

- o token retornado no login deve ser usado nesse `token_id`

## Modulos principais

### Admin Master

- `GET|POST /api/v1/admin/accounts/<token_id>`
- `GET|POST /api/v1/admin/plans/<token_id>`
- `GET|POST /api/v1/admin/modules/<token_id>`
- `GET|POST /api/v1/admin/account_modules/<token_id>`
- `GET|POST /api/v1/admin/master_users/<token_id>`
- `GET|POST /api/v1/admin/bootstrap/<token_id>`
- `GET /api/v1/admin/schema-compatibility/<token_id>`

### Tenant

- `GET /api/v1/tenant/metadata/<token_id>`
- `GET|POST /api/v1/tenant/companies/<token_id>`
- `GET|POST /api/v1/tenant/roles/<token_id>`
- `GET|POST /api/v1/tenant/permissions/<token_id>`
- `GET|POST /api/v1/tenant/role_permissions/<token_id>`
- `GET|POST /api/v1/tenant/users/<token_id>`
- `POST /api/v1/tenant/bootstrap/<token_id>`

### Diario de Obra

- `GET|POST|PUT /api/v1/diary/<token_id>`
- `GET /api/v1/diary/detail/<diary_id>/<token_id>`
- `GET /api/v1/diary/<diary_id>/<token_id>`  `alias recomendado`
- `GET /api/v1/diary/export/<diary_id>/<token_id>`
- `GET /api/v1/diary/<diary_id>/export/<token_id>`  `alias recomendado`
- `GET /api/v1/diary/monthly-export/<token_id>`
- `POST /api/v1/diary/approve/<diary_id>/<token_id>`
- `POST /api/v1/diary/<diary_id>/approve/<token_id>`  `alias recomendado`
- `POST /api/v1/diary/reject/<diary_id>/<token_id>`
- `POST /api/v1/diary/<diary_id>/reject/<token_id>`  `alias recomendado`

### Produção

- `GET|POST|PUT|DELETE /api/v1/production/<token_id>`

### Operacional

- `GET /api/v1/dashboard/operational/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/projects/<token_id>`
- `POST /api/v1/projects/setup/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/teams/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/team_members/<token_id>`
- `GET /api/v1/reports/project-diaries/<token_id>`
- `GET /api/v1/reports/projects/diaries/<token_id>`  `alias recomendado`
- `GET /api/v1/reports/project-summary/<token_id>`
- `GET /api/v1/reports/projects/summary/<token_id>`  `alias recomendado`

### Lancamentos auxiliares do diario

- `GET|POST|PUT|DELETE /api/v1/daily/occurrences/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/daily/activities/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/daily/labor/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/daily/materials/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/daily/equipments/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/daily/files/<token_id>`
- `GET|POST|PUT|DELETE /api/v1/daily/signatures/<token_id>`

### Auditoria e indicadores

- `GET /api/v1/audit/logs/<token_id>`
- `GET /api/v1/audit/summary/<token_id>`
- `GET /api/v1/audit/timeline/project/<token_id>`
- `GET /api/v1/audit/projects/timeline/<token_id>`  `alias recomendado`
- `GET /api/v1/audit/timeline/diary/<token_id>`
- `GET /api/v1/audit/diaries/timeline/<token_id>`  `alias recomendado`
- `GET /api/v1/dashboard/user-summary/<token_id>`
- `GET /api/v1/dashboard/users/summary/<token_id>`  `alias recomendado`
- `GET /api/v1/indicators/diary/by-user/<token_id>`
- `GET /api/v1/indicators/production/by-user/<token_id>`

## Observacoes

- a API retorna `NXResult` em todas as rotas principais
- os modulos `admin`, `tenant`, `operational`, `diary` e `production` ja usam padronizacao central de mensagens de sucesso/erro por helper interno, incluindo respostas de leitura em boa parte do backend
- para descobrir rapidamente campos obrigatorios por fluxo, use `GET /api/v1/payloads`
- para ver exemplos completos de body, use `GET /api/v1/examples`
- para filtros e query params de leitura, use `GET /api/v1/queries`
- para exemplos de resposta por modulo, use `GET /api/v1/responses`
- para consumir tudo agrupado por modulo, use `GET /api/v1/catalog`
- o catalogo modular agora tambem informa `capabilities` e `permissions` sugeridas por modulo
- `GET /api/v1/admin/bootstrap/<token_id>` ajuda a inspecionar `schema_version` e `master_seed`
- `POST /api/v1/admin/bootstrap/<token_id>` executa seed master inicial de forma idempotente
- `GET /api/v1/admin/schema-compatibility/<token_id>` verifica tabelas minimas e metadata esperada do banco master
- para receber o catalogo ja filtrado pelo escopo/permissoes do token, use `GET /api/v1/catalog/<token_id>`
- para consultar usuario, escopo, permissoes e modulos visiveis sem carregar o catalogo inteiro, use `GET /api/v1/session/<token_id>`
- para consultar acoes resolvidas como `can_create_diary` e `can_manage_projects`, use `GET /api/v1/capabilities/<token_id>`
- para montar menu/navegacao por grupos como `cadastros`, `operacao`, `visao_geral` e `governanca`, use `GET /api/v1/feature-map/<token_id>`
- o `feature-map` agora tambem devolve `home_route` por grupo e `route` por item
- o `feature-map` agora tambem devolve `label` e `icon` por grupo e item
- o `feature-map` agora tambem devolve `order` e `priority` por grupo e item
- para descobrir acoes como `edit`, `approve`, `delete` e `export` por registro, use `GET /api/v1/context-actions/<entity>/<record_id>/<token_id>`
- para reduzir chamadas do frontend, use `GET /api/v1/screen-context/<token_id>` ou `GET /api/v1/screen-context/<entity>/<record_id>/<token_id>`
- o `screen-context` agora tambem devolve `page_title`, `breadcrumbs`, `empty_state`, `primary_action`, `secondary_actions` e `page_actions`
- `page_actions` entrega acoes principais de topo como `novo`, `editar`, `aprovar`, `exportar` ou `voltar`, ja resolvidas para a sessao e para o registro quando houver
- `primary_action` destaca o CTA principal da tela e `secondary_actions` entrega o restante das acoes ja ordenadas
- as acoes agora tambem podem trazer `intent`, `style` e `confirmation` para orientar CTA principal, acao destrutiva e confirmacoes de operacao
- as acoes agora tambem podem trazer `api_action` e `http_method` para diferenciar navegacao de chamada direta de endpoint
- as acoes de backend agora tambem podem trazer `api_path` com o endpoint recomendado para execucao
- as acoes de backend agora tambem podem trazer `required_params` e `payload_schema` para orientar token, query string e body esperado
- entidades contextuais ja cobertas: `diary`, `project`, `production`, `team`, `team_member`, `occurrence`, `activity`, `labor`, `material`, `equipment`, `file` e `signature`
- os payloads agora cobrem tambem `projects`, `teams`, `team_members` e os CRUDs auxiliares de diario
- a referencia agora cobre tambem os cadastros `admin` e `tenant`
- para ambiente local, o arquivo `_config.server.json` continua aceito
- para Railway, prefira variaveis de ambiente e `sslmode=require`
- smoke test sugerido: `docs/api-smoke-test.md`
- a propria API agora tambem expone a sequencia sugerida em `GET /api/v1/smoke-plan`
- a propria API agora tambem expone checks basicos de seguranca em `GET /api/v1/security-check`
- checklist Railway: `docs/railway-checklist.md`
- exemplos de curl: `docs/api-curl-examples.md`
- sequencia de bootstrap: `docs/bootstrap-sequence.md`

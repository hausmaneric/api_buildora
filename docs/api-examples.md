# API Examples

## Endpoints de apoio

- `GET /api/v1/about`
- `GET /api/v1/routes`
- `GET /api/v1/conventions`
- `GET /api/v1/smoke-plan`
- `GET /api/v1/security-check`
- `GET /api/v1/environment`
- `GET /api/v1/payloads`
- `GET /api/v1/examples`
- `GET /api/v1/queries`
- `GET /api/v1/responses`
- `GET /api/v1/catalog`
- `GET /api/v1/catalog/<token_id>`
- `GET /api/v1/session/<token_id>`
- `GET /api/v1/capabilities/<token_id>`
- `GET /api/v1/feature-map/<token_id>`
- `GET /api/v1/context-actions/<entity>/<record_id>/<token_id>`
- `GET /api/v1/screen-context/<token_id>`
- `GET /api/v1/screen-context/<entity>/<record_id>/<token_id>`
- `GET /api/v1/admin/bootstrap/<token_id>`
- `POST /api/v1/admin/bootstrap/<token_id>`
- `GET /api/v1/admin/schema-compatibility/<token_id>`

- `GET /api/v1/ready` agora pode devolver:
  - `database_ping`
  - `database_config.valid`
  - `database_config.mode`
  - `database_config.issues`

- `GET /api/v1/environment` agora tambem expone:
  - `database.validation.valid`
  - `database.validation.mode`
  - `database.validation.issues`

## Payloads

- `GET /api/v1/payloads` retorna uma referencia objetiva com:
  - campos obrigatorios
  - campos opcionais
  - headers obrigatorios quando houver

- fluxos cobertos inicialmente:
  - `admin.accounts.create`
  - `admin.plans.create`
  - `admin.modules.create`
  - `admin.account_modules.create`
  - `admin.master_users.create`
  - `auth.master_login`
  - `auth.tenant_login`
  - `tenant.companies.create`
  - `tenant.roles.create`
  - `tenant.permissions.create`
  - `tenant.role_permissions.create`
  - `tenant.users.create`
  - `tenant.bootstrap`
  - `projects.setup`
  - `projects.create`
  - `projects.update`
  - `teams.create`
  - `teams.update`
  - `team_members.create`
  - `team_members.update`
  - `diary.create`
  - `diary.update`
  - `production.create`
  - `production.update`
  - `daily.occurrences.create`
  - `daily.occurrences.update`
  - `daily.activities.create`
  - `daily.activities.update`
  - `daily.labor.create`
  - `daily.labor.update`
  - `daily.materials.create`
  - `daily.materials.update`
  - `daily.equipments.create`
  - `daily.equipments.update`
  - `daily.files.create`
  - `daily.files.update`
  - `daily.signatures.create`
  - `daily.signatures.update`

## Queries

- `GET /api/v1/queries` retorna os filtros esperados para rotas de consulta, incluindo:
  - listagens `admin` e `tenant`
  - `diary`
  - `production`
  - `reports`
  - `audit`
  - `dashboard`
  - `indicators`
  - CRUDs auxiliares do diario por `daily_log_id`

## Responses

- `GET /api/v1/responses` retorna exemplos de resposta no padrao `NXResult`, incluindo:
  - padrao de listagem
  - padrao de cadastro
  - detalhe de diario
  - dashboard operacional
  - resumo por obra
  - auditoria

## Catalog

- `GET /api/v1/catalog` entrega a documentacao agrupada por modulo:
  - `admin`
  - `auth`
  - `tenant`
  - `operational`
  - `diary`
  - `production`

- cada modulo retorna junto:
  - capabilities
  - permissions
  - rotas
  - payloads
  - queries
  - responses
  - examples

- `GET /api/v1/catalog/<token_id>` entrega o mesmo catalogo com resolucao por autenticacao:
  - `scope`
  - `permissions` do token
  - `visible` por modulo
  - `granted_permissions` por modulo

- `GET /api/v1/session/<token_id>` entrega um resumo de sessao autenticada com:
  - `user_id`
  - `scope`
  - `account_code`
  - `permissions`
  - `visible_modules`

- `GET /api/v1/capabilities/<token_id>` entrega a resolucao de acoes da sessao, por exemplo:
  - `can_manage_projects`
  - `can_create_diary`
  - `can_approve_diary`
  - `can_manage_production`
  - `can_view_audit`

- `GET /api/v1/feature-map/<token_id>` entrega um mapa pronto para navegacao por grupos:
  - `cadastros`
  - `operacao`
  - `visao_geral`
  - `governanca`

- cada grupo do `feature-map` agora tambem pode trazer:
  - `order`
  - `priority`
  - `home_route`
  - `label`
  - `icon`
  - `items.<item>.order`
  - `items.<item>.priority`
  - `items.<item>.route`
  - `items.<item>.label`
  - `items.<item>.icon`

- `GET /api/v1/context-actions/<entity>/<record_id>/<token_id>` entrega acoes por registro.
  - entidades iniciais:
    - `diary`
    - `project`
    - `production`
    - `team`
    - `team_member`
    - `occurrence`
    - `activity`
    - `labor`
    - `material`
    - `equipment`
    - `file`
    - `signature`
  - acoes tipicas:
    - `view`
    - `edit`
    - `delete`
    - `approve`
    - `reject`
    - `export`
    - `reports`
    - `dashboard`

- `GET /api/v1/screen-context/<token_id>` agrega em uma chamada:
  - `session`
  - `capabilities`
  - `feature_map`
  - `page_title`
  - `breadcrumbs`
  - `empty_state`
  - `primary_action`
  - `secondary_actions`
  - `page_actions`

- `GET /api/v1/screen-context/<entity>/<record_id>/<token_id>` agrega em uma chamada:
  - `session`
  - `capabilities`
  - `feature_map`
  - `context`
  - `page_title`
  - `breadcrumbs`
  - `empty_state`
  - `primary_action`
  - `secondary_actions`
  - `page_actions`

- `page_actions` foi pensado para a barra superior da tela e ja pode trazer acoes como:
  - `Abrir dashboard`
  - `Nova obra`
  - `Novo diário`
  - `Editar`
  - `Aprovar`
  - `Exportar`
  - `Voltar`

- `primary_action` entrega a principal chamada para acao da tela.
- `secondary_actions` entrega as demais acoes ja ordenadas por prioridade.
- cada acao tambem pode trazer:
  - `intent` como `primary`, `neutral` ou `danger`
  - `style` como `solid`, `outline` ou `ghost`
  - `confirmation` para acoes sensiveis como aprovar, reprovar e excluir
  - `api_action` para indicar se a acao chama endpoint diretamente
  - `http_method` com verbos como `GET`, `POST` e `DELETE`
  - `api_path` com o endpoint sugerido para a operacao quando a acao for de backend
  - `required_params` para indicar parametros obrigatorios como `token_id`, `record_id` ou `id`
  - `payload_schema` para indicar se o backend espera query string ou body e quais campos sao obrigatorios

## Fluxos principais

### Bootstrap master

```json
{
  "schema_version": "1.0.0",
  "plan_name": "Plano Base",
  "plan_description": "Plano inicial da plataforma",
  "plan_price": 0,
  "max_companies": 1,
  "max_users": 25,
  "max_works": 10,
  "max_storage_mb": 2048,
  "admin_name": "Master Admin",
  "admin_login": "admin",
  "admin_password": "123456",
  "admin_email": "master@obrax.com",
  "modules": [
    {
      "code": "DIARY",
      "name": "Diario de Obra",
      "description": "Modulo de diario"
    },
    {
      "code": "PRODUCTION",
      "name": "Producao",
      "description": "Modulo de producao"
    }
  ]
}
```

### Login master

```json
{
  "login": "admin",
  "password": "123456"
}
```

### Login tenant

Header:

```text
X-Account-Code: demo
```

Body:

```json
{
  "email": "admin@empresa.com",
  "password": "123456"
}
```

### Bootstrap tenant

```json
{
  "company_code": "EMP001",
  "company_document": "12345678000199",
  "corporate_name": "Empresa Demo",
  "fantasy_name": "Demo",
  "phone": "11999999999",
  "email": "contato@demo.com",
  "zipcode": "01001000",
  "address": "Rua Exemplo",
  "number": "100",
  "district": "Centro",
  "city": "Sao Paulo",
  "state": "SP",
  "admin_name": "Administrador",
  "admin_email": "admin@demo.com",
  "admin_password": "123456"
}
```

### Setup inicial da obra

```json
{
  "project_name": "Obra Demo",
  "project_code": "OBR001",
  "client_name": "Cliente Demo",
  "company_id": 1,
  "engineer_user_id": 1,
  "address": "Rua da Obra",
  "number": "200",
  "district": "Centro",
  "city": "Sao Paulo",
  "state": "SP",
  "zipcode": "01001000",
  "budget_amount": 100000,
  "status": "active",
  "main_team_name": "Equipe Principal",
  "main_team_description": "Equipe inicial",
  "members": [
    {
      "user_id": 1,
      "member_name": "Administrador",
      "role_name": "Responsavel",
      "active": true
    }
  ]
}
```

### Criacao de diario

```json
{
  "project_id": 1,
  "work_date": "2026-05-08",
  "weather": "sunny",
  "summary": "Atividades do dia",
  "occurrences": "Sem ocorrencias",
  "status": "draft"
}
```

### Criacao de producao

```json
{
  "project_id": 1,
  "reference_date": "2026-05-08",
  "service_name": "Concretagem",
  "unit": "m3",
  "planned_quantity": 10,
  "executed_quantity": 8,
  "notes": "Execucao parcial"
}
```

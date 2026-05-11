# API Smoke Test

## Pre requisitos

- dependencias instaladas de `requirements.txt`
- banco PostgreSQL acessivel
- schema aplicado de `database/schema.sql`
- configuracao pronta por `_config.server.json` ou variaveis de ambiente

## Variaveis principais

- `OBRAX_DATABASE_URL`
- ou:
  - `OBRAX_DB_HOST`
  - `OBRAX_DB_PORT`
  - `OBRAX_DB_NAME`
  - `OBRAX_DB_USER`
  - `OBRAX_DB_PASSWORD`
  - `OBRAX_DB_SSLMODE`
- `OBRAX_SECRET_KEY`

## Ordem sugerida

1. Validar processo HTTP

- `GET /api/v1/health`
- `GET /api/v1/ready`
- `GET /api/v1/routes`
- `GET /api/v1/conventions`
- `GET /api/v1/environment`

2. Validar login master

- `POST /api/v1/auth/master/login/`
- capturar `token`

3. Validar cadastros master

- `GET /api/v1/admin/plans/<token_id>`
- `GET /api/v1/admin/modules/<token_id>`
- `GET /api/v1/admin/accounts/<token_id>`

4. Validar login tenant

- `POST /api/v1/auth/tenant/login/`
- header `X-Account-Code`
- capturar `token`

5. Validar bootstrap tenant

- `GET /api/v1/tenant/metadata/<token_id>`
- `POST /api/v1/tenant/bootstrap/<token_id>`

6. Validar operacao basica

- `GET /api/v1/projects/<token_id>`
- `POST /api/v1/projects/setup/<token_id>`
- `GET /api/v1/diary/<token_id>`
- `POST /api/v1/diary/<token_id>`
- `GET /api/v1/production/<token_id>`
- `POST /api/v1/production/<token_id>`

7. Validar consulta e observabilidade

- `GET /api/v1/dashboard/operational/<token_id>`
- `GET /api/v1/dashboard/users/summary/<token_id>`
- `GET /api/v1/audit/logs/<token_id>`
- `GET /api/v1/reports/projects/summary/<token_id>`

## Resultado esperado

- todas as rotas retornando `NXResult`
- `status = true` nas operacoes esperadas
- `error = false`
- mensagens coerentes com a operacao

## Observacao local

No ambiente atual, a importacao completa da app ainda depende de `psycopg2` estar disponivel no runtime.
Sem essa dependencia instalada, a validacao fica limitada a parse estatico da arvore `source`.

## Testes automatizados minimos

- suite inicial em `tests/`
- execucao sugerida:

```text
python -m unittest discover -s tests -v
```

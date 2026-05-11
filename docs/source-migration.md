# Migracao para o padrao `source`

## Objetivo

Alinhar o Obrax API ao padrao usado em `C:\developer.workspace\peopleware\Quartzo_API\source`.

## Estrutura criada

- `source/app.py`
- `source/controller/`
- `source/logic/`
- `source/data/models/`
- `source/data/sql/`
- `source/core/config/`
- `source/core/system/`

## Estado atual

- entrypoint novo em `source/app.py`
- controllers novos e enxutos em `source/controller`
- logica separada em `source/logic`
- models proprios em `source/data/models`
- SQL proprio em `source/data/sql`
- infraestrutura propria em `source/core/system`:
  - `auth.py`
  - `database.py`
  - `express.py`
  - `security.py`
  - `utils.py`

## Runtime

- entrypoint principal: `app.py`
- app interna: `source/app.py`
- healthcheck: `GET /api/v1/health`
- catalogo de rotas: `GET /api/v1/routes`
- guia rapido: `docs/api-quickstart.md`
- status do legado: `docs/legacy-status.md`
- deploy Railway continua usando `Procfile` com `gunicorn app:app`

## Observacao

Nesta etapa a migracao deixou de depender estruturalmente de `classes`, `models`, `data` e `controller` antigos dentro da arvore `source`.
O legado ainda pode permanecer no repositorio como historico paralelo, mas a base principal da API ja esta concentrada em `source`.

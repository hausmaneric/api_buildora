# Obrax API

## Base ativa

A base principal da API esta em:

- `source/app.py`
- `source/controller/`
- `source/logic/`
- `source/data/`
- `source/core/`

O entrypoint raiz continua em:

- `app.py`

Esse arquivo apenas sobe a app nova baseada em `source`.

## Legado preservado

As pastas abaixo ainda permanecem no repositorio como legado preservado e referencia historica:

- `classes/`
- `controller/`
- `models/`

Elas nao sao mais a base principal da API nova.

Avisos locais de legado:

- `classes/README-LEGACY.md`
- `controller/README-LEGACY.md`
- `models/README-LEGACY.md`

## Documentacao principal

- `docs/source-migration.md`
- `docs/api-quickstart.md`
- `docs/api-smoke-test.md`
- `docs/api-curl-examples.md`
- `docs/api-examples.md`
- `docs/bootstrap-sequence.md`
- `docs/railway-checklist.md`
- `docs/legacy-removal-checklist.md`

## Endpoints de apoio

- `GET /api/v1/health`
- `GET /api/v1/ready`
- `GET /api/v1/routes`
- `GET /api/v1/conventions`
- `GET /api/v1/environment`
- `GET /api/v1/about`

## Deploy

- `Procfile`: `web: gunicorn app:app`
- `runtime.txt`: `python-3.12.8`
- dependencias: `requirements.txt`
- `railway.json`: start command e healthcheck para Railway
- `.env.example`: referencia de variaveis para producao

## Variaveis Railway

- `OBRAX_API_NAME`
- `OBRAX_API_VERSION`
- `OBRAX_DATABASE_URL`
- `OBRAX_DB_HOST`
- `OBRAX_DB_PORT`
- `OBRAX_DB_NAME`
- `OBRAX_DB_USER`
- `OBRAX_DB_PASSWORD`
- `OBRAX_DB_SSLMODE`
- `OBRAX_SECRET_KEY`
- `OBRAX_SETUP_KEY`

Em producao, prefira usar `OBRAX_DATABASE_URL` fornecida pelo Postgres do Railway.
Use `OBRAX_SETUP_KEY` apenas no setup inicial via endpoint e troque ou remova apos a inicializacao.

# Railway Checklist

## Runtime

- `Procfile`: `web: gunicorn app:app`
- `runtime.txt`: `python-3.12.8`
- dependencias em `requirements.txt`

## Banco

- criar PostgreSQL no Railway
- aplicar `database/schema.sql`
- usar `sslmode=require` em producao

## Configuracao

- preferir `OBRAX_DATABASE_URL`
- definir `OBRAX_SECRET_KEY`
- evitar segredos reais em `_config.server.json`

## Verificacoes apos deploy

- `GET /api/v1/health`
- `GET /api/v1/ready`
- `GET /api/v1/routes`
- `GET /api/v1/conventions`
- `GET /api/v1/environment`

## Primeira rodada funcional

- login master
- login tenant
- bootstrap tenant
- setup inicial da obra
- criacao de diario
- criacao de producao

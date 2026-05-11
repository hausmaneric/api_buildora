# Deploy no Railway

## Variáveis esperadas

- `PORT`
- `OBRAX_DATABASE_URL` ou o conjunto `OBRAX_DB_HOST`, `OBRAX_DB_PORT`, `OBRAX_DB_NAME`, `OBRAX_DB_USER`, `OBRAX_DB_PASSWORD`, `OBRAX_DB_SSLMODE`
- `OBRAX_SECRET_KEY`

## Passos sugeridos

1. Criar o serviço da API no Railway.
2. Adicionar um banco PostgreSQL no mesmo projeto.
3. Configurar as variáveis de ambiente.
4. Aplicar o schema de `database/schema.sql`.
5. Subir a aplicação usando o `Procfile`.

## Observações

- A API já está preparada para usar `OBRAX_DATABASE_URL` completo no padrão do Railway.
- Para produção, prefira `sslmode=require`.
- O arquivo `_config.server.json` fica útil para ambiente local e não deve carregar segredos reais em repositório público.

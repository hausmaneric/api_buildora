# Bootstrap Sequence

## Ordem minima sugerida

1. Subir a API
2. Validar `GET /api/v1/health`
3. Validar `GET /api/v1/ready`
4. Fazer login master
5. Criar ou consultar `plans`
6. Criar ou consultar `modules`
7. Criar `accounts`
8. Fazer login tenant com `X-Account-Code`
9. Consultar `tenant/metadata`
10. Executar `tenant/bootstrap`
11. Executar `projects/setup`
12. Criar primeiro `diary`
13. Criar primeiro `production`
14. Validar `dashboard`, `reports` e `audit`

## Resultado esperado

- ambiente tenant inicializado
- empresa principal criada
- usuario administrador criado
- obra inicial criada
- equipe principal criada
- primeiro diario registrado
- primeiro lancamento de producao registrado

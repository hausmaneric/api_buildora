# Legacy Removal Checklist

## Objetivo

Remover `classes/`, `controller/` e `models/` antigos apenas depois que a API nova em `source/` estiver validada em runtime real.

## Pre requisitos

- smoke test executado com sucesso
- validacao de login master e tenant
- validacao de bootstrap tenant
- validacao de setup inicial da obra
- validacao de diario, producao, dashboard, reports e audit
- validacao de deploy no Railway

## Checklist

1. Confirmar que `app.py` continua apontando apenas para `source.app`
2. Confirmar que nenhuma importacao do `source/` usa:
- `classes/`
- `controller/`
- `models/`
3. Validar `GET /api/v1/routes`
4. Validar `GET /api/v1/conventions`
5. Validar `GET /api/v1/environment`
6. Rodar smoke test completo
7. Fazer backup ou branch dedicado para remocao
8. Remover legado por etapas
9. Rodar smoke test novamente
10. Validar deploy no Railway novamente

## Ordem sugerida de remocao

1. `models/`
2. `controller/`
3. `classes/`

## Observacao

Se qualquer etapa de runtime falhar, a remocao deve ser pausada e corrigida antes de continuar.

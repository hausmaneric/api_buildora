# Legacy Status

## Situacao atual

A arvore nova em `source/` ja e a base principal da API.

As estruturas antigas abaixo permanecem apenas como apoio historico e transicao:

- `classes/`
- `controller/`
- `models/`

## O que ja foi consolidado em `source`

- app principal
- auth
- conexao master e tenant
- dataset/express
- models
- SQL
- controllers
- logic
- documentacao operacional

## Recomendacao

Para qualquer evolucao nova da API:

- usar `source/controller`
- usar `source/logic`
- usar `source/data/models`
- usar `source/data/sql`
- usar `source/core/system`

## Observacao

O legado ainda nao foi removido fisicamente nesta etapa para evitar quebra acidental.
A remocao deve ser feita em uma rodada separada e controlada, preferencialmente depois de smoke test real e validacao de deploy.

Checklist sugerido para essa etapa:

- `docs/legacy-removal-checklist.md`

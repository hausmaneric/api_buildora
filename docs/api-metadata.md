# Metadados da API

## Endpoint

- `GET /api/v1/tenant/metadata`

## Objetivo

Disponibilizar ao frontend um catálogo central para evitar hardcode de:

- status
- filtros suportados
- módulos do sistema
- perfis padrão
- permissões do ambiente

## Requisitos

- autenticação tenant válida
- permissão `permissions.read`
- cabeçalho `X-Account-Code`

## Estrutura retornada

- `api`
- `modules`
- `default_roles`
- `permissions`
- `roles`
- `status_catalog`
- `filters`

## Observação

Esse endpoint foi pensado para alimentar selects, filtros, badges de status e controle de acesso no frontend.

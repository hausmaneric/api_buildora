# API Curl Examples

## Health

```bash
curl -X GET http://localhost:8080/api/v1/health
```

## Environment

```bash
curl -X GET http://localhost:8080/api/v1/environment
```

## Master Login

```bash
curl -X POST http://localhost:8080/api/v1/auth/master/login/ \
  -H "Content-Type: application/json" \
  -d "{\"login\":\"admin\",\"password\":\"123456\"}"
```

## Tenant Login

```bash
curl -X POST http://localhost:8080/api/v1/auth/tenant/login/ \
  -H "Content-Type: application/json" \
  -H "X-Account-Code: demo" \
  -d "{\"email\":\"admin@empresa.com\",\"password\":\"123456\"}"
```

## Tenant Metadata

```bash
curl -X GET "http://localhost:8080/api/v1/tenant/metadata/<token_id>"
```

## Tenant Bootstrap

```bash
curl -X POST "http://localhost:8080/api/v1/tenant/bootstrap/<token_id>" \
  -H "Content-Type: application/json" \
  -d "{\"company_code\":\"EMP001\",\"company_document\":\"12345678000199\",\"corporate_name\":\"Empresa Demo\",\"fantasy_name\":\"Demo\",\"phone\":\"11999999999\",\"email\":\"contato@demo.com\",\"zipcode\":\"01001000\",\"address\":\"Rua Exemplo\",\"number\":\"100\",\"district\":\"Centro\",\"city\":\"Sao Paulo\",\"state\":\"SP\",\"admin_name\":\"Administrador\",\"admin_email\":\"admin@demo.com\",\"admin_password\":\"123456\"}"
```

## Project Setup

```bash
curl -X POST "http://localhost:8080/api/v1/projects/setup/<token_id>" \
  -H "Content-Type: application/json" \
  -d "{\"project_name\":\"Obra Demo\",\"project_code\":\"OBR001\",\"client_name\":\"Cliente Demo\",\"company_id\":1,\"engineer_user_id\":1,\"address\":\"Rua da Obra\",\"number\":\"200\",\"district\":\"Centro\",\"city\":\"Sao Paulo\",\"state\":\"SP\",\"zipcode\":\"01001000\",\"budget_amount\":100000,\"status\":\"active\",\"main_team_name\":\"Equipe Principal\",\"main_team_description\":\"Equipe inicial\",\"members\":[{\"user_id\":1,\"member_name\":\"Administrador\",\"role_name\":\"Responsavel\",\"active\":true}]}"
```

## Create Diary

```bash
curl -X POST "http://localhost:8080/api/v1/diary/<token_id>" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":1,\"work_date\":\"2026-05-08\",\"weather\":\"sunny\",\"summary\":\"Atividades do dia\",\"occurrences\":\"Sem ocorrencias\",\"status\":\"draft\"}"
```

## Create Production

```bash
curl -X POST "http://localhost:8080/api/v1/production/<token_id>" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":1,\"reference_date\":\"2026-05-08\",\"service_name\":\"Concretagem\",\"unit\":\"m3\",\"planned_quantity\":10,\"executed_quantity\":8,\"notes\":\"Execucao parcial\"}"
```

## Routes Catalog

```bash
curl -X GET http://localhost:8080/api/v1/routes
```

## Conventions

```bash
curl -X GET http://localhost:8080/api/v1/conventions
```

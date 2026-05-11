from flask import request
from app import app
from classes.auth_utils import open_tenant_connection, require_tenant_permission
from classes.next_base import NXResult
from classes.obrax_utils import write_audit_log
from classes.sql.obx_sql import (
    SQL_AUDIT_LOGS_LIST,
    SQL_AUDIT_LOGS_LIST_LIMITED,
    SQL_AUDIT_SUMMARY,
    SQL_AUDIT_TIMELINE_DIARY,
    SQL_AUDIT_TIMELINE_PROJECT,
    SQL_DASHBOARD_USER_SUMMARY,
    SQL_INDICATORS_DIARY_BY_USER,
    SQL_INDICATORS_PRODUCTION_BY_USER,
    SQL_PRODUCTION_BY_ID,
    SQL_PRODUCTION_DELETE,
    SQL_PRODUCTION_FILTERED_LIST,
    SQL_PRODUCTION_INSERT,
    SQL_PRODUCTION_UPDATE,
    SQL_PROJECT_BY_ID,
    SQL_TENANT_USER_BY_ID,
)
from models.production import ProductionEntryInput


def _tenant_connection(permission_code: str) -> tuple[NXResult, object | None]:
    auth, payload = require_tenant_permission(permission_code)
    if auth.error:
        return auth, None

    account_code = request.headers.get('X-Account-Code', '').strip()
    result, tenant, _account = open_tenant_connection(account_code)
    if result.error:
        return result, None
    result.data = {
        'auth_payload': payload,
        'account_code': account_code,
    }
    return result, tenant


def _load_project(tenant, project_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_PROJECT_BY_ID, project_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar obra da producao', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Obra da producao nao localizada')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


def _load_user(tenant, user_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_TENANT_USER_BY_ID, user_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar usuario da producao', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Usuario da producao nao localizado')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


def _load_production(tenant, production_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_PRODUCTION_BY_ID, production_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar lancamento de producao', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Lancamento de producao nao localizado')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


@app.route('/api/v1/production', methods=['GET', 'POST', 'PUT', 'DELETE'])
def production_index():
    permission = 'production.read' if request.method == 'GET' else 'production.write'
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        auth_payload = opened.data or {}
        auth_user_id = auth_payload.get('auth_payload', {}).get('user_id')

        if request.method == 'GET':
            project_id = request.args.get('project_id', type=int)
            created_by = request.args.get('created_by', type=int)
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            rs = tenant.xp_nx.FDXQuery(
                SQL_PRODUCTION_FILTERED_LIST,
                project_id,
                project_id,
                created_by,
                created_by,
                start_date,
                start_date,
                end_date,
                end_date,
            )
            if rs.error:
                result.make_error(0, 'Erro ao listar producao', rs.message)
            else:
                result.status = True
                result.data = rs.dataset.recordset

        elif request.method == 'POST':
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados invalidos enviados')
                return result.toJSON()

            payload = ProductionEntryInput.from_dict(data)
            loaded_project, project = _load_project(tenant, payload.project_id)
            if loaded_project.error:
                return loaded_project.toJSON()

            created_by = payload.created_by or auth_user_id
            if not created_by:
                result.make_error(0, 'Usuario responsavel pela producao e obrigatorio')
                return result.toJSON()

            loaded_user, user = _load_user(tenant, created_by)
            if loaded_user.error:
                return loaded_user.toJSON()

            if payload.created_by and auth_user_id and payload.created_by != auth_user_id:
                result.make_error(0, 'O usuario autenticado nao pode lancar producao por outro usuario')
                return result.toJSON()

            if project.get('company_id') and user.get('company_id') and project.get('company_id') != user.get('company_id'):
                result.make_error(0, 'Usuario da producao nao pertence a empresa da obra informada')
                return result.toJSON()

            rs = tenant.xp_nx.FDXQuery(
                SQL_PRODUCTION_INSERT,
                payload.project_id,
                payload.reference_date,
                payload.service_name,
                payload.unit,
                payload.planned_quantity,
                payload.executed_quantity,
                payload.notes,
                created_by,
            )
            if rs.error:
                result.make_error(0, 'Erro ao gravar producao', rs.message)
            else:
                record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
                write_audit_log(
                    tenant,
                    None,
                    auth_user_id,
                    'production',
                    'post',
                    'production_entries',
                    record.get('id'),
                    request.remote_addr,
                    {
                        'project_id': payload.project_id,
                        'reference_date': payload.reference_date,
                        'service_name': payload.service_name,
                        'unit': payload.unit,
                        'planned_quantity': payload.planned_quantity,
                        'executed_quantity': payload.executed_quantity,
                        'created_by': created_by,
                    },
                )
                result.status = True
                result.message = 'Producao cadastrada com sucesso'
                result.data = record if record else None

        elif request.method == 'PUT':
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados invalidos enviados')
                return result.toJSON()

            payload = ProductionEntryInput.from_dict(data)
            if not payload.id:
                result.make_error(0, 'Parametro id e obrigatorio para atualizar producao')
                return result.toJSON()

            loaded_production, production = _load_production(tenant, payload.id)
            if loaded_production.error:
                return loaded_production.toJSON()

            loaded_project, project = _load_project(tenant, payload.project_id)
            if loaded_project.error:
                return loaded_project.toJSON()

            production_owner_id = production.get('created_by')
            if production_owner_id and auth_user_id and production_owner_id != auth_user_id:
                result.make_error(0, 'O usuario autenticado nao pode alterar producao de outro usuario')
                return result.toJSON()

            loaded_user, user = _load_user(tenant, production_owner_id)
            if loaded_user.error:
                return loaded_user.toJSON()

            if project.get('company_id') and user.get('company_id') and project.get('company_id') != user.get('company_id'):
                result.make_error(0, 'Usuario responsavel pela producao nao pertence a empresa da obra informada')
                return result.toJSON()

            rs = tenant.xp_nx.FDXQuery(
                SQL_PRODUCTION_UPDATE,
                payload.project_id,
                payload.reference_date,
                payload.service_name,
                payload.unit,
                payload.planned_quantity,
                payload.executed_quantity,
                payload.notes,
                payload.id,
            )
            if rs.error:
                result.make_error(0, 'Erro ao atualizar producao', rs.message)
            else:
                record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
                write_audit_log(
                    tenant,
                    None,
                    auth_user_id,
                    'production',
                    'put',
                    'production_entries',
                    record.get('id') or payload.id,
                    request.remote_addr,
                    data,
                )
                result.status = True
                result.message = 'Producao atualizada com sucesso'
                result.data = record if record else None

        else:
            production_id = request.args.get('id', type=int)
            if not production_id:
                result.make_error(0, 'Parametro id e obrigatorio para excluir producao')
                return result.toJSON()

            loaded_production, production = _load_production(tenant, production_id)
            if loaded_production.error:
                return loaded_production.toJSON()

            production_owner_id = production.get('created_by')
            if production_owner_id and auth_user_id and production_owner_id != auth_user_id:
                result.make_error(0, 'O usuario autenticado nao pode excluir producao de outro usuario')
                return result.toJSON()

            rs = tenant.xp_nx.FDXQuery(SQL_PRODUCTION_DELETE, production_id)
            if rs.error:
                result.make_error(0, 'Erro ao excluir producao', rs.message)
            else:
                record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
                write_audit_log(
                    tenant,
                    None,
                    auth_user_id,
                    'production',
                    'delete',
                    'production_entries',
                    record.get('id') or production_id,
                    request.remote_addr,
                    {'id': production_id},
                )
                result.status = True
                result.message = 'Producao excluida com sucesso'
                result.data = record if record else None
    except Exception as e:
        result.make_error(0, 'Erro ao processar producao', str(e))
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/audit/logs', methods=['GET'])
def audit_logs():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        module = request.args.get('module', '').strip()
        action = request.args.get('action', '').strip()
        table_name = request.args.get('table_name', '').strip()
        record_id = request.args.get('record_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', default=100, type=int) or 100
        offset = request.args.get('offset', default=0, type=int) or 0
        limit = max(1, min(limit, 500))
        offset = max(0, offset)

        rs = tenant.xp_nx.FDXQuery(
            SQL_AUDIT_LOGS_LIST_LIMITED,
            module,
            module,
            action,
            action,
            table_name,
            table_name,
            record_id,
            record_id,
            start_date,
            start_date,
            end_date,
            end_date,
            limit,
            offset,
        )
        if rs.error:
            result.make_error(0, 'Erro ao listar auditoria', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/indicators/diary/by-user', methods=['GET'])
def indicators_diary_by_user():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        rs = tenant.xp_nx.FDXQuery(
            SQL_INDICATORS_DIARY_BY_USER,
            project_id,
            project_id,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if rs.error:
            result.make_error(0, 'Erro ao montar indicadores de diario por responsavel', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/indicators/production/by-user', methods=['GET'])
def indicators_production_by_user():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        rs = tenant.xp_nx.FDXQuery(
            SQL_INDICATORS_PRODUCTION_BY_USER,
            project_id,
            project_id,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if rs.error:
            result.make_error(0, 'Erro ao montar indicadores de producao por responsavel', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/dashboard/user-summary', methods=['GET'])
def dashboard_user_summary():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        rs = tenant.xp_nx.FDXQuery(
            SQL_DASHBOARD_USER_SUMMARY,
            project_id,
            project_id,
            start_date,
            start_date,
            end_date,
            end_date,
            project_id,
            project_id,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if rs.error:
            result.make_error(0, 'Erro ao montar dashboard resumido por responsavel', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/audit/summary', methods=['GET'])
def audit_summary():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        module = request.args.get('module', '').strip()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        rs = tenant.xp_nx.FDXQuery(
            SQL_AUDIT_SUMMARY,
            module,
            module,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if rs.error:
            result.make_error(0, 'Erro ao montar resumo de auditoria', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/audit/timeline/project', methods=['GET'])
def audit_timeline_project():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        project_id = request.args.get('project_id', type=int)
        limit = request.args.get('limit', default=100, type=int) or 100
        limit = max(1, min(limit, 500))
        if not project_id:
            result.make_error(0, 'Parâmetro project_id é obrigatório')
            return result.toJSON()

        project_like = f'%\"project_id\": {project_id}%'
        rs = tenant.xp_nx.FDXQuery(
            SQL_AUDIT_TIMELINE_PROJECT,
            project_id,
            project_like,
            limit,
        )
        if rs.error:
            result.make_error(0, 'Erro ao consultar timeline da obra', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/audit/timeline/diary', methods=['GET'])
def audit_timeline_diary():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        diary_id = request.args.get('diary_id', type=int)
        limit = request.args.get('limit', default=100, type=int) or 100
        limit = max(1, min(limit, 500))
        if not diary_id:
            result.make_error(0, 'Parâmetro diary_id é obrigatório')
            return result.toJSON()

        diary_like = f'%\"daily_log_id\": {diary_id}%'
        rs = tenant.xp_nx.FDXQuery(
            SQL_AUDIT_TIMELINE_DIARY,
            diary_id,
            diary_like,
            limit,
        )
        if rs.error:
            result.make_error(0, 'Erro ao consultar timeline do diário', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()

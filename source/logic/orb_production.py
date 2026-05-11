from typing import Any

from source.core.system.security import write_audit_log
from source.core.system.utils import NXResult, process_error_message, success_message
from source.data.sql.sql_obrax import (
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


def _load_project(nx: Any, project_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_PROJECT_BY_ID, project_id)
        if rs.error:
            result.make_error(0, 'Erro ao consultar obra da producao', rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, 'Obra da producao nao localizada')
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
    except Exception as e:
        result.make_error(0, 'Erro ao consultar obra da producao', str(e))
        return result, None


def _load_user(nx: Any, user_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TENANT_USER_BY_ID, user_id)
        if rs.error:
            result.make_error(0, 'Erro ao consultar usuario da producao', rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, 'Usuario da producao nao localizado')
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
    except Exception as e:
        result.make_error(0, 'Erro ao consultar usuario da producao', str(e))
        return result, None


def _load_production(nx: Any, production_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_PRODUCTION_BY_ID, production_id)
        if rs.error:
            result.make_error(0, 'Erro ao consultar lancamento de producao', rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, 'Lancamento de producao nao localizado')
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
    except Exception as e:
        result.make_error(0, 'Erro ao consultar lancamento de producao', str(e))
        return result, None


def production_list(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        project_id = int(data.get('project_id')) if data.get('project_id') else None
        created_by = int(data.get('created_by')) if data.get('created_by') else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        rs = nx.xp_nx.FDXQuery(
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
        if not rs.error:
            result.status = True
            result.message = success_message('Producao', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao listar producao', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta da producao', str(e))
    return result


def production_create(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    try:
        created_by = data.get('created_by', nx.session.userid)
        if not created_by:
            result.make_error(0, 'Usuario responsavel pela producao e obrigatorio')
            return result

        loaded_project, project = _load_project(nx, data.get('project_id'))
        if loaded_project.error:
            return loaded_project
        loaded_user, user = _load_user(nx, created_by)
        if loaded_user.error:
            return loaded_user

        if data.get('created_by') and nx.session.userid and data.get('created_by') != nx.session.userid:
            result.make_error(0, 'O usuario autenticado nao pode lancar producao por outro usuario')
            return result
        if project.get('company_id') and user.get('company_id') and project.get('company_id') != user.get('company_id'):
            result.make_error(0, 'Usuario da producao nao pertence a empresa da obra informada')
            return result

        rs = nx.xp_nx.FDXQuery(
            SQL_PRODUCTION_INSERT,
            data.get('project_id'),
            data.get('reference_date'),
            data.get('service_name'),
            data.get('unit'),
            data.get('planned_quantity', 0),
            data.get('executed_quantity', 0),
            data.get('notes'),
            created_by,
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            write_audit_log(
                nx._tenant,
                None,
                nx.session.userid,
                'production',
                'post',
                'production_entries',
                record.get('id') if record else None,
                '',
                {
                    'project_id': data.get('project_id'),
                    'reference_date': data.get('reference_date'),
                    'service_name': data.get('service_name'),
                    'unit': data.get('unit'),
                    'planned_quantity': data.get('planned_quantity', 0),
                    'executed_quantity': data.get('executed_quantity', 0),
                    'created_by': created_by,
                },
            )
            result.status = True
            result.message = success_message('Producao', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao gravar producao', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('producao', 'create'), str(e))
    return result


def production_update(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    try:
        loaded_production, production = _load_production(nx, data.get('id'))
        if loaded_production.error:
            return loaded_production
        loaded_project, project = _load_project(nx, data.get('project_id'))
        if loaded_project.error:
            return loaded_project
        owner_id = production.get('created_by')
        if owner_id and nx.session.userid and owner_id != nx.session.userid:
            result.make_error(0, 'O usuario autenticado nao pode alterar producao de outro usuario')
            return result
        loaded_user, user = _load_user(nx, owner_id)
        if loaded_user.error:
            return loaded_user
        if project.get('company_id') and user.get('company_id') and project.get('company_id') != user.get('company_id'):
            result.make_error(0, 'Usuario responsavel pela producao nao pertence a empresa da obra informada')
            return result

        rs = nx.xp_nx.FDXQuery(
            SQL_PRODUCTION_UPDATE,
            data.get('project_id'),
            data.get('reference_date'),
            data.get('service_name'),
            data.get('unit'),
            data.get('planned_quantity', 0),
            data.get('executed_quantity', 0),
            data.get('notes'),
            data.get('id'),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            write_audit_log(
                nx._tenant,
                None,
                nx.session.userid,
                'production',
                'put',
                'production_entries',
                record.get('id') if record else data.get('id'),
                '',
                data,
            )
            result.status = True
            result.message = success_message('Producao', 'update')
            result.data = record
        else:
            result.make_error(0, 'Erro ao atualizar producao', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('producao', 'update'), str(e))
    return result


def production_delete(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        loaded_production, production = _load_production(nx, int(data.get('id')))
        if loaded_production.error:
            return loaded_production
        owner_id = production.get('created_by')
        if owner_id and nx.session.userid and owner_id != nx.session.userid:
            result.make_error(0, 'O usuario autenticado nao pode excluir producao de outro usuario')
            return result

        rs = nx.xp_nx.FDXQuery(SQL_PRODUCTION_DELETE, data.get('id'))
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            write_audit_log(
                nx._tenant,
                None,
                nx.session.userid,
                'production',
                'delete',
                'production_entries',
                data.get('id'),
                '',
                {'id': data.get('id')},
            )
            result.status = True
            result.message = success_message('Producao', 'delete')
            result.data = record
        else:
            result.make_error(0, 'Erro ao excluir producao', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('producao', 'delete'), str(e))
    return result


def audit_logs_list(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        module = data.get('module', '')
        action = data.get('action', '')
        table_name = data.get('table_name', '')
        record_id = int(data.get('record_id')) if data.get('record_id') else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        limit = int(data.get('limit', 100) or 100)
        offset = int(data.get('offset', 0) or 0)
        rs = nx.xp_nx.FDXQuery(
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
        if not rs.error:
            result.status = True
            result.message = success_message('Auditoria', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao listar auditoria', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta da auditoria', str(e))
    return result


def dashboard_summary_by_user(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        project_id = int(data.get('project_id')) if data.get('project_id') else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        rs = nx.xp_nx.FDXQuery(
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
        if not rs.error:
            result.status = True
            result.message = success_message('Dashboard por responsavel', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao montar dashboard por responsavel', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de dashboard por responsavel', str(e))
    return result


def indicators_diary_by_user(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        project_id = int(data.get('project_id')) if data.get('project_id') else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        rs = nx.xp_nx.FDXQuery(
            SQL_INDICATORS_DIARY_BY_USER,
            project_id,
            project_id,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Indicadores de diario por responsavel', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao montar indicadores de diario por responsavel', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo dos indicadores de diario', str(e))
    return result


def indicators_production_by_user(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        project_id = int(data.get('project_id')) if data.get('project_id') else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        rs = nx.xp_nx.FDXQuery(
            SQL_INDICATORS_PRODUCTION_BY_USER,
            project_id,
            project_id,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Indicadores de producao por responsavel', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao montar indicadores de producao por responsavel', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo dos indicadores de producao', str(e))
    return result


def audit_summary_list(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        module = data.get('module', '')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        rs = nx.xp_nx.FDXQuery(
            SQL_AUDIT_SUMMARY,
            module,
            module,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Resumo de auditoria', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao montar resumo de auditoria', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo do resumo de auditoria', str(e))
    return result


def audit_timeline_project_list(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        project_id = int(data.get('project_id')) if data.get('project_id') else None
        limit = max(1, min(int(data.get('limit', 100) or 100), 500))
        if not project_id:
            result.make_error(0, 'Parametro project_id e obrigatorio')
            return result
        project_like = f'%\"project_id\": {project_id}%'
        rs = nx.xp_nx.FDXQuery(SQL_AUDIT_TIMELINE_PROJECT, project_id, project_like, limit)
        if not rs.error:
            result.status = True
            result.message = success_message('Timeline da obra', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao consultar timeline da obra', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo da timeline da obra', str(e))
    return result


def audit_timeline_diary_list(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        diary_id = int(data.get('diary_id')) if data.get('diary_id') else None
        limit = max(1, min(int(data.get('limit', 100) or 100), 500))
        if not diary_id:
            result.make_error(0, 'Parametro diary_id e obrigatorio')
            return result
        diary_like = f'%\"daily_log_id\": {diary_id}%'
        rs = nx.xp_nx.FDXQuery(SQL_AUDIT_TIMELINE_DIARY, diary_id, diary_like, limit)
        if not rs.error:
            result.status = True
            result.message = success_message('Timeline do diario', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao consultar timeline do diario', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo da timeline do diario', str(e))
    return result

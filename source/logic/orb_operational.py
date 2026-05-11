from typing import Any

from source.core.system.security import write_audit_log
from source.core.system.utils import NXResult, process_error_message, success_message
from source.data.sql.sql_obrax import (
    SQL_DASHBOARD_LAST_DIARIES,
    SQL_DASHBOARD_PROJECT_PRODUCTIVITY,
    SQL_DASHBOARD_SUMMARY,
    SQL_DAILY_ACTIVITIES_LIST,
    SQL_DAILY_ACTIVITY_BY_ID,
    SQL_DAILY_ACTIVITY_DELETE,
    SQL_DAILY_ACTIVITY_INSERT,
    SQL_DAILY_ACTIVITY_UPDATE,
    SQL_DAILY_EQUIPMENTS_LIST,
    SQL_DAILY_EQUIPMENT_BY_ID,
    SQL_DAILY_EQUIPMENT_DELETE,
    SQL_DAILY_EQUIPMENT_INSERT,
    SQL_DAILY_EQUIPMENT_UPDATE,
    SQL_DAILY_FILES_LIST,
    SQL_DAILY_FILE_BY_ID,
    SQL_DAILY_FILE_DELETE,
    SQL_DAILY_FILE_INSERT,
    SQL_DAILY_FILE_UPDATE,
    SQL_DAILY_LABOR_BY_ID,
    SQL_DAILY_LABOR_DELETE,
    SQL_DAILY_LABOR_INSERT,
    SQL_DAILY_LABOR_LIST,
    SQL_DAILY_LABOR_UPDATE,
    SQL_DAILY_MATERIAL_BY_ID,
    SQL_DAILY_MATERIAL_DELETE,
    SQL_DAILY_MATERIAL_INSERT,
    SQL_DAILY_MATERIAL_UPDATE,
    SQL_DAILY_MATERIALS_LIST,
    SQL_DAILY_OCCURRENCE_BY_ID,
    SQL_DAILY_OCCURRENCE_DELETE,
    SQL_DAILY_OCCURRENCE_INSERT,
    SQL_DAILY_OCCURRENCE_UPDATE,
    SQL_DAILY_OCCURRENCES_LIST,
    SQL_DAILY_SIGNATURE_BY_ID,
    SQL_DAILY_SIGNATURE_DELETE,
    SQL_DAILY_SIGNATURE_INSERT,
    SQL_DAILY_SIGNATURE_UPDATE,
    SQL_DAILY_SIGNATURES_LIST,
    SQL_DIARY_BY_ID,
    SQL_PROJECT_BY_ID,
    SQL_PROJECT_DELETE,
    SQL_PROJECT_INSERT,
    SQL_PROJECT_UPDATE,
    SQL_PROJECTS_LIST,
    SQL_REPORT_PROJECT_DIARIES,
    SQL_REPORT_PROJECT_SUMMARY,
    SQL_TEAM_BY_ID,
    SQL_TEAM_DELETE,
    SQL_TEAM_INSERT,
    SQL_TEAM_MEMBER_BY_ID,
    SQL_TEAM_MEMBER_DELETE,
    SQL_TEAM_MEMBER_INSERT,
    SQL_TEAM_MEMBER_UPDATE,
    SQL_TEAM_MEMBERS_LIST,
    SQL_TEAM_UPDATE,
    SQL_TEAMS_LIST,
    SQL_TENANT_USER_BY_ID,
)


def _tenant_scope_ok(nx: Any) -> NXResult:
    result = NXResult()
    if nx.session.scope != 'tenant':
        result.make_error(0, 'Token sem permissao tenant')
        return result
    result.status = True
    return result


def _query_list(
    nx: Any,
    sql: str,
    params: list[Any] | None = None,
    error_message: str = 'Erro ao consultar dados',
    success_entity: str = 'Registros',
) -> NXResult:
    result = _tenant_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(sql, *(params or []))
        if not rs.error:
            result.status = True
            result.message = success_message(success_entity, 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, error_message, rs.message)
    except Exception as e:
        result.make_error(0, error_message, str(e))
    return result


def _load_record(nx: Any, sql: str, item_id: int, not_found_message: str, error_message: str) -> tuple[NXResult, dict | None]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(sql, item_id)
        if rs.error:
            result.make_error(0, error_message, rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, not_found_message)
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
    except Exception as e:
        result.make_error(0, error_message, str(e))
        return result, None


def _load_diary(nx: Any, diary_id: int) -> tuple[NXResult, dict | None]:
    return _load_record(nx, SQL_DIARY_BY_ID, diary_id, 'Diario vinculado nao localizado', 'Erro ao consultar diario vinculado')


def _load_project(nx: Any, project_id: int) -> tuple[NXResult, dict | None]:
    return _load_record(nx, SQL_PROJECT_BY_ID, project_id, 'Obra vinculada nao localizada', 'Erro ao consultar obra vinculada')


def _load_team(nx: Any, team_id: int) -> tuple[NXResult, dict | None]:
    return _load_record(nx, SQL_TEAM_BY_ID, team_id, 'Equipe vinculada nao localizada', 'Erro ao consultar equipe vinculada')


def _load_user(nx: Any, user_id: int) -> tuple[NXResult, dict | None]:
    return _load_record(nx, SQL_TENANT_USER_BY_ID, user_id, 'Usuario vinculado nao localizado', 'Erro ao consultar usuario vinculado')


def _ensure_diary_writable(nx: Any, diary_id: int) -> NXResult:
    loaded, diary = _load_diary(nx, diary_id)
    if loaded.error:
        return loaded
    if diary.get('status') == 'approved':
        result = NXResult()
        result.make_error(0, 'Diario aprovado nao permite alteracoes nos lancamentos auxiliares')
        return result
    result = NXResult()
    result.status = True
    return result


def _load_aux_daily_log_id(nx: Any, sql: str, item_id: int) -> tuple[NXResult, int | None]:
    loaded, record = _load_record(nx, sql, item_id, 'Lancamento auxiliar nao localizado', 'Erro ao consultar vinculo do lancamento auxiliar')
    if loaded.error:
        return loaded, None
    return loaded, record.get('daily_log_id')


def _write_tenant_audit(nx: Any, module: str, action: str, table_name: str, record_id: Any, data: Any) -> None:
    try:
        write_audit_log(
            nx._tenant,
            None,
            nx.session.userid,
            module,
            action,
            table_name,
            record_id,
            '',
            data,
        )
    except Exception:
        pass


def _validate_project_payload(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    engineer_user_id = data.get('engineer_user_id')
    company_id = data.get('company_id')
    if engineer_user_id:
        loaded_user, user = _load_user(nx, engineer_user_id)
        if loaded_user.error:
            return loaded_user
        if company_id and user.get('company_id') and user.get('company_id') != company_id:
            result.make_error(0, 'Engenheiro informado nao pertence a empresa da obra')
            return result
    result.status = True
    return result


def _validate_team_payload(nx: Any, data: Any) -> NXResult:
    project_id = data.get('project_id')
    if not project_id:
        result = NXResult()
        result.make_error(0, 'project_id e obrigatorio')
        return result
    return _load_project(nx, project_id)[0]


def _validate_team_member_payload(nx: Any, data: Any) -> NXResult:
    team_id = data.get('team_id')
    loaded_team, team = _load_team(nx, team_id)
    if loaded_team.error:
        return loaded_team

    user_id = data.get('user_id')
    if user_id:
        loaded_user, user = _load_user(nx, user_id)
        if loaded_user.error:
            return loaded_user
        loaded_project, project = _load_project(nx, team.get('project_id'))
        if loaded_project.error:
            return loaded_project
        if project.get('company_id') and user.get('company_id') and project.get('company_id') != user.get('company_id'):
            result = NXResult()
            result.make_error(0, 'Usuario informado nao pertence a empresa da obra da equipe')
            return result

    result = NXResult()
    result.status = True
    return result


def dashboard_operational_get(nx: Any) -> NXResult:
    result = _tenant_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        summary = nx.xp_nx.FDXQuery(SQL_DASHBOARD_SUMMARY)
        last_diaries = nx.xp_nx.FDXQuery(SQL_DASHBOARD_LAST_DIARIES)
        productivity = nx.xp_nx.FDXQuery(SQL_DASHBOARD_PROJECT_PRODUCTIVITY)
        if summary.error:
            result.make_error(0, 'Erro ao montar dashboard operacional', summary.message)
        else:
            result.status = True
            result.message = success_message('Dashboard operacional', 'list')
            result.data = {
                'summary': summary.dataset.recordset[0] if summary.dataset.recordset else {},
                'last_diaries': last_diaries.dataset.recordset if not last_diaries.error else [],
                'project_productivity': productivity.dataset.recordset if not productivity.error else [],
            }
    except Exception as e:
        result.make_error(0, 'Falha no processo do dashboard operacional', str(e))
    return result


def projects_list(nx: Any) -> NXResult:
    return _query_list(nx, SQL_PROJECTS_LIST, error_message='Erro ao listar obras', success_entity='Obras')


def projects_create(nx: Any, data: Any) -> NXResult:
    result = _validate_project_payload(nx, data)
    if result.error:
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_PROJECT_INSERT,
            data.get('name'),
            data.get('code'),
            data.get('client_name'),
            data.get('company_id'),
            data.get('engineer_user_id'),
            data.get('address'),
            data.get('number'),
            data.get('district'),
            data.get('city'),
            data.get('state'),
            data.get('zipcode'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('budget_amount'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('status', 'active'),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'projects', 'post', 'projects', record.get('id') if record else None, data)
            result.status = True
            result.message = success_message('Obra', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao cadastrar obra', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('obra', 'create'), str(e))
    return result


def projects_update(nx: Any, data: Any) -> NXResult:
    result = _validate_project_payload(nx, data)
    if result.error:
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_PROJECT_UPDATE,
            data.get('name'),
            data.get('code'),
            data.get('client_name'),
            data.get('company_id'),
            data.get('engineer_user_id'),
            data.get('address'),
            data.get('number'),
            data.get('district'),
            data.get('city'),
            data.get('state'),
            data.get('zipcode'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('budget_amount'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('status', 'active'),
            data.get('id'),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'projects', 'put', 'projects', data.get('id'), data)
            result.status = True
            result.message = success_message('Obra', 'update')
            result.data = record
        else:
            result.make_error(0, 'Erro ao atualizar obra', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('obra', 'update'), str(e))
    return result


def projects_delete(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_PROJECT_DELETE, data.get('id'))
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'projects', 'delete', 'projects', data.get('id'), {'id': data.get('id')})
            result.status = True
            result.message = success_message('Obra', 'delete')
            result.data = record
        else:
            result.make_error(0, 'Erro ao excluir obra', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('obra', 'delete'), str(e))
    return result


def teams_list(nx: Any, data: dict[str, Any]) -> NXResult:
    team_project_id = int(data.get('project_id')) if data.get('project_id') else None
    return _query_list(nx, SQL_TEAMS_LIST, [team_project_id, team_project_id], 'Erro ao listar equipes', 'Equipes')


def teams_create(nx: Any, data: Any) -> NXResult:
    result = _validate_team_payload(nx, data)
    if result.error:
        return result
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TEAM_INSERT,
            data.get('project_id'),
            data.get('name'),
            data.get('description'),
            data.get('active', True),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'teams', 'post', 'teams', record.get('id') if record else None, data)
            result.status = True
            result.message = success_message('Equipe', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao cadastrar equipe', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('equipe', 'create'), str(e))
    return result


def teams_update(nx: Any, data: Any) -> NXResult:
    result = _validate_team_payload(nx, data)
    if result.error:
        return result
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TEAM_UPDATE,
            data.get('project_id'),
            data.get('name'),
            data.get('description'),
            data.get('active', True),
            data.get('id'),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'teams', 'put', 'teams', data.get('id'), data)
            result.status = True
            result.message = success_message('Equipe', 'update')
            result.data = record
        else:
            result.make_error(0, 'Erro ao atualizar equipe', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('equipe', 'update'), str(e))
    return result


def teams_delete(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TEAM_DELETE, data.get('id'))
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'teams', 'delete', 'teams', data.get('id'), {'id': data.get('id')})
            result.status = True
            result.message = success_message('Equipe', 'delete')
            result.data = record
        else:
            result.make_error(0, 'Erro ao excluir equipe', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('equipe', 'delete'), str(e))
    return result


def team_members_list(nx: Any, data: dict[str, Any]) -> NXResult:
    team_id = int(data.get('team_id')) if data.get('team_id') else None
    return _query_list(nx, SQL_TEAM_MEMBERS_LIST, [team_id, team_id], 'Erro ao listar membros da equipe', 'Membros da equipe')


def team_members_create(nx: Any, data: Any) -> NXResult:
    result = _validate_team_member_payload(nx, data)
    if result.error:
        return result
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TEAM_MEMBER_INSERT,
            data.get('team_id'),
            data.get('user_id'),
            data.get('member_name'),
            data.get('role_name'),
            data.get('active', True),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'teams', 'post', 'team_members', record.get('id') if record else None, data)
            result.status = True
            result.message = success_message('Membro da equipe', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao cadastrar membro da equipe', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('membro da equipe', 'create'), str(e))
    return result


def team_members_update(nx: Any, data: Any) -> NXResult:
    result = _validate_team_member_payload(nx, data)
    if result.error:
        return result
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TEAM_MEMBER_UPDATE,
            data.get('team_id'),
            data.get('user_id'),
            data.get('member_name'),
            data.get('role_name'),
            data.get('active', True),
            data.get('id'),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'teams', 'put', 'team_members', data.get('id'), data)
            result.status = True
            result.message = success_message('Membro da equipe', 'update')
            result.data = record
        else:
            result.make_error(0, 'Erro ao atualizar membro da equipe', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('membro da equipe', 'update'), str(e))
    return result


def team_members_delete(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TEAM_MEMBER_DELETE, data.get('id'))
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'teams', 'delete', 'team_members', data.get('id'), {'id': data.get('id')})
            result.status = True
            result.message = success_message('Membro da equipe', 'delete')
            result.data = record
        else:
            result.make_error(0, 'Erro ao excluir membro da equipe', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('membro da equipe', 'delete'), str(e))
    return result


def report_project_diaries_get(nx: Any, data: dict[str, Any]) -> NXResult:
    project_id = int(data.get('project_id')) if data.get('project_id') else None
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    return _query_list(
        nx,
        SQL_REPORT_PROJECT_DIARIES,
        [project_id, project_id, start_date, start_date, end_date, end_date],
        'Erro ao montar relatorio por obra',
        'Relatorio por obra',
    )


def report_project_summary_get(nx: Any, data: dict[str, Any]) -> NXResult:
    project_id = int(data.get('project_id')) if data.get('project_id') else None
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    return _query_list(
        nx,
        SQL_REPORT_PROJECT_SUMMARY,
        [project_id, project_id, start_date, start_date, end_date, end_date],
        'Erro ao montar resumo operacional por obra',
        'Resumo operacional por obra',
    )


def project_setup_create(nx: Any, data: Any) -> NXResult:
    result = _validate_project_payload(
        nx,
        {
            'company_id': data.get('company_id'),
            'engineer_user_id': data.get('engineer_user_id'),
        },
    )
    if result.error:
        return result

    result = NXResult()
    try:
        project_rs = nx.xp_nx.FDXQuery(
            SQL_PROJECT_INSERT,
            data.get('project_name'),
            data.get('project_code'),
            data.get('client_name'),
            data.get('company_id'),
            data.get('engineer_user_id'),
            data.get('address'),
            data.get('number'),
            data.get('district'),
            data.get('city'),
            data.get('state'),
            data.get('zipcode'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('budget_amount'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('status', 'active'),
        )
        if project_rs.error:
            result.make_error(0, 'Erro ao criar obra inicial', project_rs.message)
            return result

        project_id = project_rs.dataset.recordset[0]['id']

        team_rs = nx.xp_nx.FDXQuery(
            SQL_TEAM_INSERT,
            project_id,
            data.get('main_team_name'),
            data.get('main_team_description'),
            True,
        )
        if team_rs.error:
            result.make_error(0, 'Erro ao criar equipe principal', team_rs.message)
            return result

        team_id = team_rs.dataset.recordset[0]['id']
        created_members = []
        for member in data.get('members', []) or []:
            member_validation = _validate_team_member_payload(
                nx,
                {
                    'team_id': team_id,
                    'user_id': member.get('user_id'),
                },
            )
            if member_validation.error:
                return member_validation

            member_rs = nx.xp_nx.FDXQuery(
                SQL_TEAM_MEMBER_INSERT,
                team_id,
                member.get('user_id'),
                member.get('member_name'),
                member.get('role_name'),
                member.get('active', True),
            )
            if member_rs.error:
                result.make_error(0, 'Erro ao criar membro inicial da equipe', member_rs.message)
                return result
            created_members.append(member_rs.dataset.recordset[0]['id'])

        audit_data = {
            'project_id': project_id,
            'main_team_id': team_id,
            'team_members_ids': created_members,
        }
        _write_tenant_audit(nx, 'projects', 'setup', 'projects', project_id, audit_data)
        result.status = True
        result.message = success_message('Setup inicial da obra', 'bootstrap')
        result.data = audit_data
    except Exception as e:
        result.make_error(0, process_error_message('setup inicial da obra', 'bootstrap'), str(e))
    return result


def _aux_list(nx: Any, sql: str, daily_log_id: Any, error_message: str) -> NXResult:
    return _query_list(nx, sql, [daily_log_id, daily_log_id], error_message, 'Registros')


def _aux_create(nx: Any, data: Any, sql: str, params: list[Any], table_name: str) -> NXResult:
    writable = _ensure_diary_writable(nx, data.get('daily_log_id'))
    if writable.error:
        return writable

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(sql, *params)
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'diary', 'post', table_name, record.get('id') if record else None, data)
            result.status = True
            result.message = success_message('Registro', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao gravar lancamento auxiliar', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('lancamento auxiliar', 'create'), str(e))
    return result


def _aux_update(nx: Any, data: Any, sql: str, params: list[Any], table_name: str) -> NXResult:
    writable = _ensure_diary_writable(nx, data.get('daily_log_id'))
    if writable.error:
        return writable

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(sql, *params)
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'diary', 'put', table_name, data.get('id'), data)
            result.status = True
            result.message = success_message('Registro', 'update')
            result.data = record
        else:
            result.make_error(0, 'Erro ao atualizar lancamento auxiliar', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('lancamento auxiliar', 'update'), str(e))
    return result


def _aux_delete(nx: Any, data: Any, lookup_sql: str, delete_sql: str, table_name: str) -> NXResult:
    item_id = data.get('id')
    loaded, daily_log_id = _load_aux_daily_log_id(nx, lookup_sql, item_id)
    if loaded.error:
        return loaded
    writable = _ensure_diary_writable(nx, daily_log_id)
    if writable.error:
        return writable

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(delete_sql, item_id)
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            _write_tenant_audit(nx, 'diary', 'delete', table_name, item_id, {'id': item_id})
            result.status = True
            result.message = success_message('Registro', 'delete')
            result.data = record
        else:
            result.make_error(0, 'Erro ao excluir lancamento auxiliar', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('lancamento auxiliar', 'delete'), str(e))
    return result


def daily_occurrences_list(nx: Any, data: dict[str, Any]) -> NXResult:
    daily_log_id = int(data.get('daily_log_id')) if data.get('daily_log_id') else None
    return _aux_list(nx, SQL_DAILY_OCCURRENCES_LIST, daily_log_id, 'Erro ao listar ocorrencias do diario')


def daily_occurrences_create(nx: Any, data: Any) -> NXResult:
    return _aux_create(
        nx,
        data,
        SQL_DAILY_OCCURRENCE_INSERT,
        [data.get('daily_log_id'), data.get('occurrence_type'), data.get('title'), data.get('description'), data.get('severity'), data.get('resolved', False)],
        'daily_log_occurrences',
    )


def daily_occurrences_update(nx: Any, data: Any) -> NXResult:
    return _aux_update(
        nx,
        data,
        SQL_DAILY_OCCURRENCE_UPDATE,
        [data.get('occurrence_type'), data.get('title'), data.get('description'), data.get('severity'), data.get('resolved', False), data.get('id')],
        'daily_log_occurrences',
    )


def daily_occurrences_delete(nx: Any, data: Any) -> NXResult:
    return _aux_delete(nx, data, SQL_DAILY_OCCURRENCE_BY_ID, SQL_DAILY_OCCURRENCE_DELETE, 'daily_log_occurrences')


def daily_activities_list(nx: Any, data: dict[str, Any]) -> NXResult:
    daily_log_id = int(data.get('daily_log_id')) if data.get('daily_log_id') else None
    return _aux_list(nx, SQL_DAILY_ACTIVITIES_LIST, daily_log_id, 'Erro ao listar atividades do diario')


def daily_activities_create(nx: Any, data: Any) -> NXResult:
    return _aux_create(
        nx,
        data,
        SQL_DAILY_ACTIVITY_INSERT,
        [data.get('daily_log_id'), data.get('service_name'), data.get('quantity', 0), data.get('unit'), data.get('location'), data.get('notes')],
        'daily_log_activities',
    )


def daily_activities_update(nx: Any, data: Any) -> NXResult:
    return _aux_update(
        nx,
        data,
        SQL_DAILY_ACTIVITY_UPDATE,
        [data.get('service_name'), data.get('quantity', 0), data.get('unit'), data.get('location'), data.get('notes'), data.get('id')],
        'daily_log_activities',
    )


def daily_activities_delete(nx: Any, data: Any) -> NXResult:
    return _aux_delete(nx, data, SQL_DAILY_ACTIVITY_BY_ID, SQL_DAILY_ACTIVITY_DELETE, 'daily_log_activities')


def daily_labor_list(nx: Any, data: dict[str, Any]) -> NXResult:
    daily_log_id = int(data.get('daily_log_id')) if data.get('daily_log_id') else None
    return _aux_list(nx, SQL_DAILY_LABOR_LIST, daily_log_id, 'Erro ao listar mao de obra do diario')


def daily_labor_create(nx: Any, data: Any) -> NXResult:
    return _aux_create(
        nx,
        data,
        SQL_DAILY_LABOR_INSERT,
        [data.get('daily_log_id'), data.get('team_member_id'), data.get('worker_name'), data.get('role_name'), data.get('hours_worked', 0), data.get('present', True)],
        'daily_log_labor',
    )


def daily_labor_update(nx: Any, data: Any) -> NXResult:
    return _aux_update(
        nx,
        data,
        SQL_DAILY_LABOR_UPDATE,
        [data.get('team_member_id'), data.get('worker_name'), data.get('role_name'), data.get('hours_worked', 0), data.get('present', True), data.get('id')],
        'daily_log_labor',
    )


def daily_labor_delete(nx: Any, data: Any) -> NXResult:
    return _aux_delete(nx, data, SQL_DAILY_LABOR_BY_ID, SQL_DAILY_LABOR_DELETE, 'daily_log_labor')


def daily_materials_list(nx: Any, data: dict[str, Any]) -> NXResult:
    daily_log_id = int(data.get('daily_log_id')) if data.get('daily_log_id') else None
    return _aux_list(nx, SQL_DAILY_MATERIALS_LIST, daily_log_id, 'Erro ao listar materiais do diario')


def daily_materials_create(nx: Any, data: Any) -> NXResult:
    return _aux_create(
        nx,
        data,
        SQL_DAILY_MATERIAL_INSERT,
        [data.get('daily_log_id'), data.get('material_name'), data.get('movement_type'), data.get('quantity', 0), data.get('unit'), data.get('notes')],
        'daily_log_materials',
    )


def daily_materials_update(nx: Any, data: Any) -> NXResult:
    return _aux_update(
        nx,
        data,
        SQL_DAILY_MATERIAL_UPDATE,
        [data.get('material_name'), data.get('movement_type'), data.get('quantity', 0), data.get('unit'), data.get('notes'), data.get('id')],
        'daily_log_materials',
    )


def daily_materials_delete(nx: Any, data: Any) -> NXResult:
    return _aux_delete(nx, data, SQL_DAILY_MATERIAL_BY_ID, SQL_DAILY_MATERIAL_DELETE, 'daily_log_materials')


def daily_equipments_list(nx: Any, data: dict[str, Any]) -> NXResult:
    daily_log_id = int(data.get('daily_log_id')) if data.get('daily_log_id') else None
    return _aux_list(nx, SQL_DAILY_EQUIPMENTS_LIST, daily_log_id, 'Erro ao listar equipamentos do diario')


def daily_equipments_create(nx: Any, data: Any) -> NXResult:
    return _aux_create(
        nx,
        data,
        SQL_DAILY_EQUIPMENT_INSERT,
        [data.get('daily_log_id'), data.get('equipment_name'), data.get('status'), data.get('hours_used', 0), data.get('notes')],
        'daily_log_equipments',
    )


def daily_equipments_update(nx: Any, data: Any) -> NXResult:
    return _aux_update(
        nx,
        data,
        SQL_DAILY_EQUIPMENT_UPDATE,
        [data.get('equipment_name'), data.get('status'), data.get('hours_used', 0), data.get('notes'), data.get('id')],
        'daily_log_equipments',
    )


def daily_equipments_delete(nx: Any, data: Any) -> NXResult:
    return _aux_delete(nx, data, SQL_DAILY_EQUIPMENT_BY_ID, SQL_DAILY_EQUIPMENT_DELETE, 'daily_log_equipments')


def daily_files_list(nx: Any, data: dict[str, Any]) -> NXResult:
    daily_log_id = int(data.get('daily_log_id')) if data.get('daily_log_id') else None
    return _aux_list(nx, SQL_DAILY_FILES_LIST, daily_log_id, 'Erro ao listar arquivos do diario')


def daily_files_create(nx: Any, data: Any) -> NXResult:
    return _aux_create(
        nx,
        data,
        SQL_DAILY_FILE_INSERT,
        [data.get('daily_log_id'), data.get('file_name'), data.get('file_type'), data.get('file_url'), data.get('file_size_bytes', 0), data.get('notes')],
        'daily_log_files',
    )


def daily_files_update(nx: Any, data: Any) -> NXResult:
    return _aux_update(
        nx,
        data,
        SQL_DAILY_FILE_UPDATE,
        [data.get('file_name'), data.get('file_type'), data.get('file_url'), data.get('file_size_bytes', 0), data.get('notes'), data.get('id')],
        'daily_log_files',
    )


def daily_files_delete(nx: Any, data: Any) -> NXResult:
    return _aux_delete(nx, data, SQL_DAILY_FILE_BY_ID, SQL_DAILY_FILE_DELETE, 'daily_log_files')


def daily_signatures_list(nx: Any, data: dict[str, Any]) -> NXResult:
    daily_log_id = int(data.get('daily_log_id')) if data.get('daily_log_id') else None
    return _aux_list(nx, SQL_DAILY_SIGNATURES_LIST, daily_log_id, 'Erro ao listar assinaturas do diario')


def daily_signatures_create(nx: Any, data: Any) -> NXResult:
    return _aux_create(
        nx,
        data,
        SQL_DAILY_SIGNATURE_INSERT,
        [data.get('daily_log_id'), data.get('signed_by_user_id'), data.get('signer_name'), data.get('signature_type'), data.get('signature_data')],
        'daily_log_signatures',
    )


def daily_signatures_update(nx: Any, data: Any) -> NXResult:
    return _aux_update(
        nx,
        data,
        SQL_DAILY_SIGNATURE_UPDATE,
        [data.get('signed_by_user_id'), data.get('signer_name'), data.get('signature_type'), data.get('signature_data'), data.get('id')],
        'daily_log_signatures',
    )


def daily_signatures_delete(nx: Any, data: Any) -> NXResult:
    return _aux_delete(nx, data, SQL_DAILY_SIGNATURE_BY_ID, SQL_DAILY_SIGNATURE_DELETE, 'daily_log_signatures')

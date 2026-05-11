from typing import Any

from source.core.system.security import write_audit_log
from source.core.system.utils import NXResult, process_error_message, success_message
from source.data.sql.sql_obrax import (
    SQL_DAILY_ACTIVITIES_LIST,
    SQL_DAILY_EQUIPMENTS_LIST,
    SQL_DAILY_FILES_LIST,
    SQL_DAILY_LABOR_LIST,
    SQL_DAILY_MATERIALS_LIST,
    SQL_DAILY_OCCURRENCES_LIST,
    SQL_DAILY_SIGNATURES_LIST,
    SQL_DIARY_BY_ID,
    SQL_DIARY_FILTERED_LIST,
    SQL_DIARY_INSERT,
    SQL_DIARY_STATUS_UPDATE,
    SQL_DIARY_UPDATE,
    SQL_PROJECT_BY_ID,
    SQL_TENANT_USER_BY_ID,
)


def _load_diary(nx: Any, diary_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_DIARY_BY_ID, diary_id)
        if rs.error:
            result.make_error(0, 'Erro ao consultar diario', rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, 'Diario nao localizado')
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
    except Exception as e:
        result.make_error(0, 'Erro ao consultar diario', str(e))
        return result, None


def _load_project(nx: Any, project_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_PROJECT_BY_ID, project_id)
        if rs.error:
            result.make_error(0, 'Erro ao consultar obra', rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, 'Obra nao localizada')
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
    except Exception as e:
        result.make_error(0, 'Erro ao consultar obra', str(e))
        return result, None


def _load_user(nx: Any, user_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TENANT_USER_BY_ID, user_id)
        if rs.error:
            result.make_error(0, 'Erro ao consultar usuario do diario', rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, 'Usuario do diario nao localizado')
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
    except Exception as e:
        result.make_error(0, 'Erro ao consultar usuario do diario', str(e))
        return result, None


def _diary_sections(nx: Any, diary_id: int) -> dict[str, list[Any]]:
    occurrences = nx.xp_nx.FDXQuery(SQL_DAILY_OCCURRENCES_LIST, diary_id, diary_id)
    activities = nx.xp_nx.FDXQuery(SQL_DAILY_ACTIVITIES_LIST, diary_id, diary_id)
    labor = nx.xp_nx.FDXQuery(SQL_DAILY_LABOR_LIST, diary_id, diary_id)
    materials = nx.xp_nx.FDXQuery(SQL_DAILY_MATERIALS_LIST, diary_id, diary_id)
    equipments = nx.xp_nx.FDXQuery(SQL_DAILY_EQUIPMENTS_LIST, diary_id, diary_id)
    files = nx.xp_nx.FDXQuery(SQL_DAILY_FILES_LIST, diary_id, diary_id)
    signatures = nx.xp_nx.FDXQuery(SQL_DAILY_SIGNATURES_LIST, diary_id, diary_id)
    return {
        'occurrences': occurrences.dataset.recordset if not occurrences.error else [],
        'activities': activities.dataset.recordset if not activities.error else [],
        'labor': labor.dataset.recordset if not labor.error else [],
        'materials': materials.dataset.recordset if not materials.error else [],
        'equipments': equipments.dataset.recordset if not equipments.error else [],
        'files': files.dataset.recordset if not files.error else [],
        'signatures': signatures.dataset.recordset if not signatures.error else [],
    }


def diary_list(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        project_id = int(data.get('project_id')) if data.get('project_id') else None
        status = data.get('status', '')
        created_by = int(data.get('created_by')) if data.get('created_by') else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        rs = nx.xp_nx.FDXQuery(
            SQL_DIARY_FILTERED_LIST,
            project_id,
            project_id,
            status,
            status,
            created_by,
            created_by,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Diarios', 'list')
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao listar diario', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta do diario', str(e))
    return result


def diary_create(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    try:
        created_by = data.get('created_by', nx.session.userid)
        if not created_by:
            result.make_error(0, 'Usuario responsavel pelo diario e obrigatorio')
            return result

        loaded_project, project = _load_project(nx, data.get('project_id'))
        if loaded_project.error:
            return loaded_project

        loaded_user, user = _load_user(nx, created_by)
        if loaded_user.error:
            return loaded_user

        if data.get('created_by') and nx.session.userid and data.get('created_by') != nx.session.userid:
            result.make_error(0, 'O usuario autenticado nao pode criar diario por outro usuario')
            return result

        if project.get('company_id') and user.get('company_id') and project.get('company_id') != user.get('company_id'):
            result.make_error(0, 'Usuario do diario nao pertence a empresa da obra informada')
            return result

        rs = nx.xp_nx.FDXQuery(
            SQL_DIARY_INSERT,
            data.get('project_id'),
            data.get('work_date'),
            data.get('weather'),
            data.get('summary'),
            data.get('occurrences'),
            data.get('status', 'draft'),
            created_by,
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            write_audit_log(
                nx._tenant,
                None,
                nx.session.userid,
                'diary',
                'post',
                'daily_logs',
                record.get('id') if record else None,
                '',
                {
                    'project_id': data.get('project_id'),
                    'work_date': data.get('work_date'),
                    'status': data.get('status', 'draft'),
                    'created_by': created_by,
                },
            )
            result.status = True
            result.message = success_message('Diario de obra', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao gravar diario', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('diario de obra', 'create'), str(e))
    return result


def diary_update(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    try:
        loaded, diary = _load_diary(nx, data.get('id'))
        if loaded.error:
            return loaded
        if diary.get('status') == 'approved':
            result.make_error(0, 'Diario aprovado nao pode mais ser alterado')
            return result

        rs = nx.xp_nx.FDXQuery(
            SQL_DIARY_UPDATE,
            data.get('weather'),
            data.get('summary'),
            data.get('occurrences'),
            data.get('status', 'draft'),
            data.get('id'),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else None
            write_audit_log(
                nx._tenant,
                None,
                nx.session.userid,
                'diary',
                'put',
                'daily_logs',
                record.get('id') if record else data.get('id'),
                '',
                data,
            )
            result.status = True
            result.message = success_message('Diario', 'update')
            result.data = record
        else:
            result.make_error(0, 'Erro ao atualizar diario', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('diario', 'update'), str(e))
    return result


def diary_detail(nx: Any, diary_id: int) -> NXResult:
    result, diary = _load_diary(nx, diary_id)
    if result.error:
        return result

    try:
        result = NXResult()
        result.status = True
        result.message = success_message('Diario', 'status')
        result.data = {
            'diary': diary,
            **_diary_sections(nx, diary_id),
        }
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta do diario completo', str(e))
    return result


def diary_export(nx: Any, diary_id: int) -> NXResult:
    result, diary = _load_diary(nx, diary_id)
    if result.error:
        return result

    try:
        result = NXResult()
        result.status = True
        result.message = success_message('Exportacao do diario', 'status')
        result.data = {
            'export_type': 'daily_log',
            'generated_at': diary.get('updated_at') or diary.get('created_at'),
            'daily_log': diary,
            'sections': _diary_sections(nx, diary_id),
        }
    except Exception as e:
        result.make_error(0, 'Falha no processo de exportacao do diario', str(e))
    return result


def diary_monthly_export(nx: Any, data: dict[str, Any]) -> NXResult:
    result = NXResult()
    try:
        project_id = int(data.get('project_id')) if data.get('project_id') else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if not project_id:
            result.make_error(0, 'Parametro project_id e obrigatorio')
            return result

        loaded_project, project = _load_project(nx, project_id)
        if loaded_project.error:
            return loaded_project

        rs = nx.xp_nx.FDXQuery(
            SQL_DIARY_FILTERED_LIST,
            project_id,
            project_id,
            '',
            '',
            None,
            None,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if rs.error:
            result.make_error(0, 'Erro ao consultar diarios do periodo', rs.message)
            return result

        diaries_data = []
        totals = {
            'diaries': 0,
            'occurrences': 0,
            'activities': 0,
            'labor': 0,
            'materials': 0,
            'equipments': 0,
            'files': 0,
            'signatures': 0,
        }
        for diary in rs.dataset.recordset:
            sections = _diary_sections(nx, diary['id'])
            totals['diaries'] += 1
            totals['occurrences'] += len(sections['occurrences'])
            totals['activities'] += len(sections['activities'])
            totals['labor'] += len(sections['labor'])
            totals['materials'] += len(sections['materials'])
            totals['equipments'] += len(sections['equipments'])
            totals['files'] += len(sections['files'])
            totals['signatures'] += len(sections['signatures'])
            diaries_data.append({'diary': diary, 'sections': sections})

        result.status = True
        result.message = success_message('Exportacao mensal do diario', 'status')
        result.data = {
            'export_type': 'monthly_daily_log_report',
            'project': project,
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'totals': totals,
            'diaries': diaries_data,
        }
    except Exception as e:
        result.make_error(0, 'Falha no processo de exportacao mensal do diario', str(e))
    return result


def diary_approve(nx: Any, diary_id: int) -> NXResult:
    result, diary = _load_diary(nx, diary_id)
    if result.error:
        return result
    if diary.get('status') == 'approved':
        result = NXResult()
        result.make_error(0, 'Diario ja esta aprovado')
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_DIARY_STATUS_UPDATE, 'approved', diary_id)
        if not rs.error:
            write_audit_log(
                nx._tenant,
                None,
                nx.session.userid,
                'diary',
                'approve',
                'daily_logs',
                diary_id,
                '',
                {'daily_log_id': diary_id, 'from_status': diary.get('status'), 'to_status': 'approved'},
            )
            result.status = True
            result.message = success_message('Diario', 'update')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
        else:
            result.make_error(0, 'Erro ao aprovar diario', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('aprovacao do diario', 'update'), str(e))
    return result


def diary_reject(nx: Any, diary_id: int) -> NXResult:
    result, diary = _load_diary(nx, diary_id)
    if result.error:
        return result
    if diary.get('status') == 'approved':
        result = NXResult()
        result.make_error(0, 'Diario aprovado nao pode ser reprovado')
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_DIARY_STATUS_UPDATE, 'rejected', diary_id)
        if not rs.error:
            write_audit_log(
                nx._tenant,
                None,
                nx.session.userid,
                'diary',
                'reject',
                'daily_logs',
                diary_id,
                '',
                {'daily_log_id': diary_id, 'from_status': diary.get('status'), 'to_status': 'rejected'},
            )
            result.status = True
            result.message = success_message('Diario', 'update')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
        else:
            result.make_error(0, 'Erro ao reprovar diario', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('reprovacao do diario', 'update'), str(e))
    return result

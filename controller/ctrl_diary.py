from flask import request
from app import app
from classes.auth_utils import open_tenant_connection, require_tenant_permission
from classes.next_base import NXResult
from classes.obrax_utils import write_audit_log
from classes.sql.obx_sql import (
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
from models.diary import DailyLogFilter, DailyLogInput, DailyLogUpdateInput


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


def _load_diary(tenant, diary_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_DIARY_BY_ID, diary_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar diário', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Diário não localizado')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


def _load_project(tenant, project_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_PROJECT_BY_ID, project_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar obra', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Obra não localizada')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


def _load_user(tenant, user_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_TENANT_USER_BY_ID, user_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar usuario do diario', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Usuario do diario nao localizado')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


@app.route('/api/v1/diary', methods=['GET', 'POST', 'PUT'])
def diary_index():
    permission = 'diary.read' if request.method == 'GET' else 'diary.write'
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        if request.method == 'GET':
            filter_data = DailyLogFilter(
                project_id=request.args.get('project_id', type=int),
                status=request.args.get('status', ''),
                created_by=request.args.get('created_by', type=int),
                start_date=request.args.get('start_date'),
                end_date=request.args.get('end_date'),
            )
            rs = tenant.xp_nx.FDXQuery(
                SQL_DIARY_FILTERED_LIST,
                filter_data.project_id,
                filter_data.project_id,
                filter_data.status,
                filter_data.status,
                filter_data.created_by,
                filter_data.created_by,
                filter_data.start_date,
                filter_data.start_date,
                filter_data.end_date,
                filter_data.end_date,
            )
            if rs.error:
                result.make_error(0, 'Erro ao listar diários', rs.message)
            else:
                result.status = True
                result.data = rs.dataset.recordset
        elif request.method == 'POST':
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
            else:
                payload = DailyLogInput.from_dict(data)
                loaded_project, project = _load_project(tenant, payload.project_id)
                if loaded_project.error:
                    return loaded_project.toJSON()

                auth_payload = opened.data or {}
                auth_user_id = auth_payload.get('auth_payload', {}).get('user_id')
                created_by = payload.created_by or auth_user_id
                if not created_by:
                    result.make_error(0, 'Usuario responsavel pelo diario e obrigatorio')
                    return result.toJSON()

                loaded_user, user = _load_user(tenant, created_by)
                if loaded_user.error:
                    return loaded_user.toJSON()

                if payload.created_by and auth_user_id and payload.created_by != auth_user_id:
                    result.make_error(0, 'O usuario autenticado nao pode criar diario por outro usuario')
                    return result.toJSON()

                if project.get('company_id') and user.get('company_id') and project.get('company_id') != user.get('company_id'):
                    result.make_error(0, 'Usuario do diario nao pertence a empresa da obra informada')
                    return result.toJSON()
                rs = tenant.xp_nx.FDXQuery(
                    SQL_DIARY_INSERT,
                    payload.project_id,
                    payload.work_date,
                    payload.weather,
                    payload.summary,
                    payload.occurrences,
                    payload.status,
                    created_by,
                )
                if rs.error:
                    result.make_error(0, 'Erro ao gravar diário', rs.message)
                else:
                    record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
                    write_audit_log(
                        tenant,
                        None,
                        auth_user_id,
                        'diary',
                        'post',
                        'daily_logs',
                        record.get('id'),
                        request.remote_addr,
                        {
                            'project_id': payload.project_id,
                            'work_date': payload.work_date,
                            'status': payload.status,
                            'created_by': created_by,
                        },
                    )
                    result.status = True
                    result.message = 'Diário de obra cadastrado com sucesso'
                    result.data = record if record else None
        else:
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
            else:
                payload = DailyLogUpdateInput.from_dict(data)
                auth_payload = opened.data or {}
                auth_user_id = auth_payload.get('auth_payload', {}).get('user_id')
                loaded, diary = _load_diary(tenant, payload.id)
                if loaded.error:
                    result = loaded
                elif diary.get('status') == 'approved':
                    result.make_error(0, 'Diário aprovado não pode mais ser alterado')
                else:
                    rs = tenant.xp_nx.FDXQuery(
                        SQL_DIARY_UPDATE,
                        payload.weather,
                        payload.summary,
                        payload.occurrences,
                        payload.status,
                        payload.id,
                    )
                    if rs.error:
                        result.make_error(0, 'Erro ao atualizar diário', rs.message)
                    else:
                        record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
                        write_audit_log(
                            tenant,
                            None,
                            auth_user_id,
                            'diary',
                            'put',
                            'daily_logs',
                            record.get('id') or payload.id,
                            request.remote_addr,
                            data,
                        )
                        result.status = True
                        result.message = 'Diário atualizado com sucesso'
                        result.data = record if record else None
    except Exception as e:
        result.make_error(0, 'Erro ao processar diário de obra', str(e))
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/diary/<int:diary_id>', methods=['GET'])
def diary_detail(diary_id: int):
    opened, tenant = _tenant_connection('diary.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        loaded, diary = _load_diary(tenant, diary_id)
        if loaded.error:
            result = loaded
        else:
            occurrences = tenant.xp_nx.FDXQuery(SQL_DAILY_OCCURRENCES_LIST, diary_id, diary_id)
            activities = tenant.xp_nx.FDXQuery(SQL_DAILY_ACTIVITIES_LIST, diary_id, diary_id)
            labor = tenant.xp_nx.FDXQuery(SQL_DAILY_LABOR_LIST, diary_id, diary_id)
            materials = tenant.xp_nx.FDXQuery(SQL_DAILY_MATERIALS_LIST, diary_id, diary_id)
            equipments = tenant.xp_nx.FDXQuery(SQL_DAILY_EQUIPMENTS_LIST, diary_id, diary_id)
            files = tenant.xp_nx.FDXQuery(SQL_DAILY_FILES_LIST, diary_id, diary_id)
            signatures = tenant.xp_nx.FDXQuery(SQL_DAILY_SIGNATURES_LIST, diary_id, diary_id)

            result.status = True
            result.data = {
                'diary': diary,
                'occurrences': occurrences.dataset.recordset if not occurrences.error else [],
                'activities': activities.dataset.recordset if not activities.error else [],
                'labor': labor.dataset.recordset if not labor.error else [],
                'materials': materials.dataset.recordset if not materials.error else [],
                'equipments': equipments.dataset.recordset if not equipments.error else [],
                'files': files.dataset.recordset if not files.error else [],
                'signatures': signatures.dataset.recordset if not signatures.error else [],
            }
    except Exception as e:
        result.make_error(0, 'Erro ao consultar diário completo', str(e))
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/diary/<int:diary_id>/export', methods=['GET'])
def diary_export(diary_id: int):
    opened, tenant = _tenant_connection('diary.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        loaded, diary = _load_diary(tenant, diary_id)
        if loaded.error:
            result = loaded
        else:
            occurrences = tenant.xp_nx.FDXQuery(SQL_DAILY_OCCURRENCES_LIST, diary_id, diary_id)
            activities = tenant.xp_nx.FDXQuery(SQL_DAILY_ACTIVITIES_LIST, diary_id, diary_id)
            labor = tenant.xp_nx.FDXQuery(SQL_DAILY_LABOR_LIST, diary_id, diary_id)
            materials = tenant.xp_nx.FDXQuery(SQL_DAILY_MATERIALS_LIST, diary_id, diary_id)
            equipments = tenant.xp_nx.FDXQuery(SQL_DAILY_EQUIPMENTS_LIST, diary_id, diary_id)
            files = tenant.xp_nx.FDXQuery(SQL_DAILY_FILES_LIST, diary_id, diary_id)
            signatures = tenant.xp_nx.FDXQuery(SQL_DAILY_SIGNATURES_LIST, diary_id, diary_id)

            result.status = True
            result.data = {
                'export_type': 'daily_log',
                'generated_at': diary.get('updated_at') or diary.get('created_at'),
                'daily_log': diary,
                'sections': {
                    'occurrences': occurrences.dataset.recordset if not occurrences.error else [],
                    'activities': activities.dataset.recordset if not activities.error else [],
                    'labor': labor.dataset.recordset if not labor.error else [],
                    'materials': materials.dataset.recordset if not materials.error else [],
                    'equipments': equipments.dataset.recordset if not equipments.error else [],
                    'files': files.dataset.recordset if not files.error else [],
                    'signatures': signatures.dataset.recordset if not signatures.error else [],
                },
            }
    except Exception as e:
        result.make_error(0, 'Erro ao exportar estrutura do diário', str(e))
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/diary/monthly-export', methods=['GET'])
def diary_monthly_export():
    opened, tenant = _tenant_connection('diary.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not project_id:
            result.make_error(0, 'Parâmetro project_id é obrigatório')
            return result.toJSON()

        loaded_project, project = _load_project(tenant, project_id)
        if loaded_project.error:
            return loaded_project.toJSON()

        diaries_rs = tenant.xp_nx.FDXQuery(
            SQL_DIARY_FILTERED_LIST,
            project_id,
            project_id,
            '',
            '',
            start_date,
            start_date,
            end_date,
            end_date,
        )

        if diaries_rs.error:
            result.make_error(0, 'Erro ao consultar diários do período', diaries_rs.message)
        else:
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

            for diary in diaries_rs.dataset.recordset:
                diary_id = diary['id']
                occurrences = tenant.xp_nx.FDXQuery(SQL_DAILY_OCCURRENCES_LIST, diary_id, diary_id)
                activities = tenant.xp_nx.FDXQuery(SQL_DAILY_ACTIVITIES_LIST, diary_id, diary_id)
                labor = tenant.xp_nx.FDXQuery(SQL_DAILY_LABOR_LIST, diary_id, diary_id)
                materials = tenant.xp_nx.FDXQuery(SQL_DAILY_MATERIALS_LIST, diary_id, diary_id)
                equipments = tenant.xp_nx.FDXQuery(SQL_DAILY_EQUIPMENTS_LIST, diary_id, diary_id)
                files = tenant.xp_nx.FDXQuery(SQL_DAILY_FILES_LIST, diary_id, diary_id)
                signatures = tenant.xp_nx.FDXQuery(SQL_DAILY_SIGNATURES_LIST, diary_id, diary_id)

                occ_list = occurrences.dataset.recordset if not occurrences.error else []
                act_list = activities.dataset.recordset if not activities.error else []
                labor_list = labor.dataset.recordset if not labor.error else []
                mat_list = materials.dataset.recordset if not materials.error else []
                equip_list = equipments.dataset.recordset if not equipments.error else []
                file_list = files.dataset.recordset if not files.error else []
                sig_list = signatures.dataset.recordset if not signatures.error else []

                totals['diaries'] += 1
                totals['occurrences'] += len(occ_list)
                totals['activities'] += len(act_list)
                totals['labor'] += len(labor_list)
                totals['materials'] += len(mat_list)
                totals['equipments'] += len(equip_list)
                totals['files'] += len(file_list)
                totals['signatures'] += len(sig_list)

                diaries_data.append({
                    'diary': diary,
                    'sections': {
                        'occurrences': occ_list,
                        'activities': act_list,
                        'labor': labor_list,
                        'materials': mat_list,
                        'equipments': equip_list,
                        'files': file_list,
                        'signatures': sig_list,
                    },
                })

            result.status = True
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
        result.make_error(0, 'Erro ao exportar relatório mensal do diário', str(e))
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/diary/<int:diary_id>/approve', methods=['POST'])
def diary_approve(diary_id: int):
    opened, tenant = _tenant_connection('diary.approve')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        loaded, diary = _load_diary(tenant, diary_id)
        if loaded.error:
            result = loaded
        elif diary.get('status') == 'approved':
            result.make_error(0, 'Diário já está aprovado')
        else:
            rs = tenant.xp_nx.FDXQuery(SQL_DIARY_STATUS_UPDATE, 'approved', diary_id)
            if rs.error:
                result.make_error(0, 'Erro ao aprovar diário', rs.message)
            else:
                auth_payload = opened.data or {}
                write_audit_log(
                    tenant,
                    None,
                    auth_payload.get('auth_payload', {}).get('user_id'),
                    'diary',
                    'approve',
                    'daily_logs',
                    diary_id,
                    request.remote_addr,
                    {
                        'daily_log_id': diary_id,
                        'from_status': diary.get('status'),
                        'to_status': 'approved',
                    },
                )
                result.status = True
                result.message = 'Diário aprovado com sucesso'
                result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/diary/<int:diary_id>/reject', methods=['POST'])
def diary_reject(diary_id: int):
    opened, tenant = _tenant_connection('diary.approve')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        loaded, diary = _load_diary(tenant, diary_id)
        if loaded.error:
            result = loaded
        elif diary.get('status') == 'approved':
            result.make_error(0, 'Diário aprovado não pode ser reprovado')
        else:
            rs = tenant.xp_nx.FDXQuery(SQL_DIARY_STATUS_UPDATE, 'rejected', diary_id)
            if rs.error:
                result.make_error(0, 'Erro ao reprovar diário', rs.message)
            else:
                auth_payload = opened.data or {}
                write_audit_log(
                    tenant,
                    None,
                    auth_payload.get('auth_payload', {}).get('user_id'),
                    'diary',
                    'reject',
                    'daily_logs',
                    diary_id,
                    request.remote_addr,
                    {
                        'daily_log_id': diary_id,
                        'from_status': diary.get('status'),
                        'to_status': 'rejected',
                    },
                )
                result.status = True
                result.message = 'Diário reprovado com sucesso'
                result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()

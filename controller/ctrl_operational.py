from flask import request
from app import app
from classes.auth_utils import open_tenant_connection, require_tenant_permission
from classes.next_base import NXResult
from classes.obrax_utils import write_audit_log
from classes.sql.obx_sql import (
    SQL_DASHBOARD_LAST_DIARIES,
    SQL_DASHBOARD_PROJECT_PRODUCTIVITY,
    SQL_DASHBOARD_SUMMARY,
    SQL_DAILY_ACTIVITIES_LIST,
    SQL_DAILY_ACTIVITY_BY_ID,
    SQL_DAILY_ACTIVITY_INSERT,
    SQL_DAILY_ACTIVITY_UPDATE,
    SQL_DAILY_ACTIVITY_DELETE,
    SQL_DAILY_EQUIPMENTS_LIST,
    SQL_DAILY_EQUIPMENT_BY_ID,
    SQL_DAILY_EQUIPMENT_INSERT,
    SQL_DAILY_EQUIPMENT_UPDATE,
    SQL_DAILY_EQUIPMENT_DELETE,
    SQL_DAILY_FILES_LIST,
    SQL_DAILY_FILE_BY_ID,
    SQL_DAILY_FILE_INSERT,
    SQL_DAILY_FILE_UPDATE,
    SQL_DAILY_FILE_DELETE,
    SQL_DAILY_LABOR_BY_ID,
    SQL_DAILY_LABOR_INSERT,
    SQL_DAILY_LABOR_LIST,
    SQL_DAILY_LABOR_UPDATE,
    SQL_DAILY_LABOR_DELETE,
    SQL_DAILY_MATERIAL_BY_ID,
    SQL_DAILY_MATERIAL_INSERT,
    SQL_DAILY_MATERIALS_LIST,
    SQL_DAILY_MATERIAL_UPDATE,
    SQL_DAILY_MATERIAL_DELETE,
    SQL_DAILY_OCCURRENCE_BY_ID,
    SQL_DAILY_OCCURRENCE_INSERT,
    SQL_DAILY_OCCURRENCES_LIST,
    SQL_DAILY_OCCURRENCE_UPDATE,
    SQL_DAILY_OCCURRENCE_DELETE,
    SQL_DAILY_SIGNATURE_BY_ID,
    SQL_DAILY_SIGNATURES_LIST,
    SQL_DAILY_SIGNATURE_INSERT,
    SQL_DAILY_SIGNATURE_UPDATE,
    SQL_DAILY_SIGNATURE_DELETE,
    SQL_DIARY_BY_ID,
    SQL_PROJECT_BY_ID,
    SQL_PROJECTS_LIST,
    SQL_PROJECT_INSERT,
    SQL_PROJECT_UPDATE,
    SQL_PROJECT_DELETE,
    SQL_REPORT_PROJECT_DIARIES,
    SQL_REPORT_PROJECT_SUMMARY,
    SQL_TEAM_INSERT,
    SQL_TEAM_BY_ID,
    SQL_TEAM_MEMBERS_LIST,
    SQL_TEAM_MEMBER_BY_ID,
    SQL_TEAM_MEMBER_INSERT,
    SQL_TEAM_MEMBER_UPDATE,
    SQL_TEAM_MEMBER_DELETE,
    SQL_TEAM_UPDATE,
    SQL_TEAM_DELETE,
    SQL_TEAMS_LIST,
    SQL_TENANT_USER_BY_ID,
)
from models.operational import (
    DailyActivityInput,
    DailyEquipmentInput,
    DailyFileInput,
    DailyLaborInput,
    DailyMaterialInput,
    DailyOccurrenceInput,
    DailySignatureInput,
    ProjectInput,
    ProjectSetupInput,
    TeamInput,
    TeamMemberInput,
)


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
        result.make_error(0, 'Erro ao consultar diário vinculado', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Diário vinculado não localizado')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


def _load_project(tenant, project_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_PROJECT_BY_ID, project_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar obra vinculada', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Obra vinculada não localizada')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


def _load_team(tenant, team_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_TEAM_BY_ID, team_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar equipe vinculada', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Equipe vinculada não localizada')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


def _load_user(tenant, user_id: int) -> tuple[NXResult, dict | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(SQL_TENANT_USER_BY_ID, user_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar usuário vinculado', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Usuário vinculado não localizado')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0]


def _ensure_diary_writable(tenant, diary_id: int) -> NXResult:
    loaded, diary = _load_diary(tenant, diary_id)
    if loaded.error:
        return loaded
    if diary.get('status') == 'approved':
        blocked = NXResult()
        blocked.make_error(0, 'Diário aprovado não permite alterações nos lançamentos auxiliares')
        return blocked
    ok = NXResult()
    ok.status = True
    return ok


def _load_aux_daily_log_id(tenant, load_sql: str, item_id: int) -> tuple[NXResult, int | None]:
    result = NXResult()
    rs = tenant.xp_nx.FDXQuery(load_sql, item_id)
    if rs.error:
        result.make_error(0, 'Erro ao consultar vínculo do lançamento auxiliar', rs.message)
        return result, None
    if rs.dataset.recordcount == 0:
        result.make_error(0, 'Lançamento auxiliar não localizado')
        return result, None
    ok = NXResult()
    ok.status = True
    return ok, rs.dataset.recordset[0].get('daily_log_id')


def _validate_project_payload(tenant, payload: ProjectInput) -> NXResult:
    result = NXResult()
    if payload.engineer_user_id:
        loaded_user, user = _load_user(tenant, payload.engineer_user_id)
        if loaded_user.error:
            return loaded_user
        if payload.company_id and user.get('company_id') and user.get('company_id') != payload.company_id:
            result.make_error(0, 'Engenheiro informado não pertence à empresa da obra')
            return result
    result.status = True
    return result


def _validate_team_payload(tenant, payload: TeamInput) -> NXResult:
    return _load_project(tenant, payload.project_id)[0]


def _validate_team_member_payload(tenant, payload: TeamMemberInput) -> NXResult:
    loaded_team, team = _load_team(tenant, payload.team_id)
    if loaded_team.error:
        return loaded_team

    if payload.user_id:
        loaded_user, user = _load_user(tenant, payload.user_id)
        if loaded_user.error:
            return loaded_user

        loaded_project, project = _load_project(tenant, team.get('project_id'))
        if loaded_project.error:
            return loaded_project

        project_company_id = project.get('company_id')
        user_company_id = user.get('company_id')
        if project_company_id and user_company_id and project_company_id != user_company_id:
            result = NXResult()
            result.make_error(0, 'Usuário informado não pertence à empresa da obra da equipe')
            return result

    ok = NXResult()
    ok.status = True
    return ok


def _list_or_insert(
    permission_read: str,
    permission_write: str,
    list_sql: str,
    insert_sql: str,
    payload_factory,
    payload_mapper,
    query_param_name: str | None = None,
):
    permission = permission_read if request.method == 'GET' else permission_write
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        data = None
        item_id = None
        if request.method == 'GET':
            if query_param_name:
                query_value = request.args.get(query_param_name, type=int)
                rs = tenant.xp_nx.FDXQuery(list_sql, query_value, query_value)
            else:
                rs = tenant.xp_nx.FDXQuery(list_sql)
            if rs.error:
                result.make_error(0, 'Erro ao listar dados operacionais', rs.message)
            else:
                result.status = True
                result.data = rs.dataset.recordset
        else:
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
            else:
                payload = payload_factory.from_dict(data)
                rs = tenant.xp_nx.FDXQuery(insert_sql, *payload_mapper(payload))
                if rs.error:
                    result.make_error(0, 'Erro ao gravar dados operacionais', rs.message)
                else:
                    result.status = True
                    result.message = 'Registro gravado com sucesso'
                    result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()


def _crud_resource(
    permission_read: str,
    permission_write: str,
    list_sql: str,
    insert_sql: str,
    update_sql: str,
    delete_sql: str,
    payload_factory,
    insert_mapper,
    update_mapper,
    query_param_name: str | None = None,
    delete_parent_sql: str | None = None,
    audit_module: str | None = None,
    audit_table: str | None = None,
    write_validator=None,
):
    permission = permission_read if request.method == 'GET' else permission_write
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        if request.method == 'GET':
            if query_param_name:
                query_value = request.args.get(query_param_name, type=int)
                rs = tenant.xp_nx.FDXQuery(list_sql, query_value, query_value)
            else:
                rs = tenant.xp_nx.FDXQuery(list_sql)
        elif request.method == 'POST':
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
                return result.toJSON()
            payload = payload_factory.from_dict(data)
            if write_validator:
                validation = write_validator(tenant, payload)
                if validation.error:
                    return validation.toJSON()
            daily_log_id = getattr(payload, 'daily_log_id', None)
            if daily_log_id:
                writable = _ensure_diary_writable(tenant, daily_log_id)
                if writable.error:
                    return writable.toJSON()
            rs = tenant.xp_nx.FDXQuery(insert_sql, *insert_mapper(payload))
        elif request.method == 'PUT':
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
                return result.toJSON()
            payload = payload_factory.from_dict(data)
            if write_validator:
                validation = write_validator(tenant, payload)
                if validation.error:
                    return validation.toJSON()
            daily_log_id = getattr(payload, 'daily_log_id', None)
            if daily_log_id:
                writable = _ensure_diary_writable(tenant, daily_log_id)
                if writable.error:
                    return writable.toJSON()
            rs = tenant.xp_nx.FDXQuery(update_sql, *update_mapper(payload))
        else:
            item_id = request.args.get('id', type=int)
            if not item_id:
                result.make_error(0, 'Parâmetro id é obrigatório')
                return result.toJSON()
            if delete_parent_sql:
                loaded, daily_log_id = _load_aux_daily_log_id(tenant, delete_parent_sql, item_id)
                if loaded.error:
                    return loaded.toJSON()
                writable = _ensure_diary_writable(tenant, daily_log_id)
                if writable.error:
                    return writable.toJSON()
            rs = tenant.xp_nx.FDXQuery(delete_sql, item_id)

        if rs.error:
            result.make_error(0, 'Erro ao processar dados operacionais', rs.message)
        else:
            record_id = rs.dataset.recordset[0].get('id') if rs.dataset.recordset else item_id
            if request.method != 'GET' and audit_module and audit_table:
                auth_payload = opened.data or {}
                write_audit_log(
                    tenant,
                    None,
                    auth_payload.get('auth_payload', {}).get('user_id'),
                    audit_module,
                    request.method.lower(),
                    audit_table,
                    record_id,
                    request.remote_addr,
                    data if request.method in ['POST', 'PUT'] else {'id': item_id},
                )
            result.status = True
            if request.method == 'GET':
                result.data = rs.dataset.recordset
            else:
                result.message = 'Operação realizada com sucesso'
                result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/dashboard/operational', methods=['GET'])
def dashboard_operational():
    opened, tenant = _tenant_connection('dashboard.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        summary = tenant.xp_nx.FDXQuery(SQL_DASHBOARD_SUMMARY)
        last_diaries = tenant.xp_nx.FDXQuery(SQL_DASHBOARD_LAST_DIARIES)
        productivity = tenant.xp_nx.FDXQuery(SQL_DASHBOARD_PROJECT_PRODUCTIVITY)

        if summary.error:
            result.make_error(0, 'Erro ao montar dashboard operacional', summary.message)
        else:
            result.status = True
            result.data = {
                'summary': summary.dataset.recordset[0] if summary.dataset.recordset else {},
                'last_diaries': last_diaries.dataset.recordset if not last_diaries.error else [],
                'project_productivity': productivity.dataset.recordset if not productivity.error else [],
            }
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/projects', methods=['GET', 'POST', 'PUT', 'DELETE'])
def projects():
    return _crud_resource(
        'projects.read',
        'projects.write',
        SQL_PROJECTS_LIST,
        SQL_PROJECT_INSERT,
        SQL_PROJECT_UPDATE,
        SQL_PROJECT_DELETE,
        ProjectInput,
        lambda p: [
            p.name,
            p.code,
            p.client_name,
            p.company_id,
            p.engineer_user_id,
            p.address,
            p.number,
            p.district,
            p.city,
            p.state,
            p.zipcode,
            p.latitude,
            p.longitude,
            p.budget_amount,
            p.start_date,
            p.end_date,
            p.status,
        ],
        lambda p: [
            p.name,
            p.code,
            p.client_name,
            p.company_id,
            p.engineer_user_id,
            p.address,
            p.number,
            p.district,
            p.city,
            p.state,
            p.zipcode,
            p.latitude,
            p.longitude,
            p.budget_amount,
            p.start_date,
            p.end_date,
            p.status,
            p.id,
        ],
        audit_module='projects',
        audit_table='projects',
        write_validator=_validate_project_payload,
    )


@app.route('/api/v1/teams', methods=['GET', 'POST', 'PUT', 'DELETE'])
def teams():
    return _crud_resource(
        'teams.read',
        'teams.write',
        SQL_TEAMS_LIST,
        SQL_TEAM_INSERT,
        SQL_TEAM_UPDATE,
        SQL_TEAM_DELETE,
        TeamInput,
        lambda p: [p.project_id, p.name, p.description, p.active],
        lambda p: [p.project_id, p.name, p.description, p.active, p.id],
        audit_module='teams',
        audit_table='teams',
        write_validator=_validate_team_payload,
    )


@app.route('/api/v1/team_members', methods=['GET', 'POST', 'PUT', 'DELETE'])
def team_members():
    return _crud_resource(
        'teams.read',
        'teams.write',
        SQL_TEAM_MEMBERS_LIST,
        SQL_TEAM_MEMBER_INSERT,
        SQL_TEAM_MEMBER_UPDATE,
        SQL_TEAM_MEMBER_DELETE,
        TeamMemberInput,
        lambda p: [p.team_id, p.user_id, p.member_name, p.role_name, p.active],
        lambda p: [p.team_id, p.user_id, p.member_name, p.role_name, p.active, p.id],
        audit_module='teams',
        audit_table='team_members',
        write_validator=_validate_team_member_payload,
    )


@app.route('/api/v1/reports/project-diaries', methods=['GET'])
def report_project_diaries():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        rs = tenant.xp_nx.FDXQuery(
            SQL_REPORT_PROJECT_DIARIES,
            project_id,
            project_id,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if rs.error:
            result.make_error(0, 'Erro ao montar relatório por obra', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/reports/project-summary', methods=['GET'])
def report_project_summary():
    opened, tenant = _tenant_connection('reports.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        rs = tenant.xp_nx.FDXQuery(
            SQL_REPORT_PROJECT_SUMMARY,
            project_id,
            project_id,
            start_date,
            start_date,
            end_date,
            end_date,
        )
        if rs.error:
            result.make_error(0, 'Erro ao montar resumo operacional por obra', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/projects/setup', methods=['POST'])
def project_setup():
    opened, tenant = _tenant_connection('projects.write')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        data = request.get_json(silent=True)
        if not data:
            result.make_error(0, 'Dados inválidos enviados')
            return result.toJSON()

        payload = ProjectSetupInput.from_dict(data)

        project_validation = _validate_project_payload(
            tenant,
            ProjectInput(
                name=payload.project_name,
                code=payload.project_code,
                client_name=payload.client_name,
                company_id=payload.company_id,
                engineer_user_id=payload.engineer_user_id,
                address=payload.address,
                number=payload.number,
                district=payload.district,
                city=payload.city,
                state=payload.state,
                zipcode=payload.zipcode,
                latitude=payload.latitude,
                longitude=payload.longitude,
                budget_amount=payload.budget_amount,
                start_date=payload.start_date,
                end_date=payload.end_date,
                status=payload.status,
            ),
        )
        if project_validation.error:
            return project_validation.toJSON()

        project_rs = tenant.xp_nx.FDXQuery(
            SQL_PROJECT_INSERT,
            payload.project_name,
            payload.project_code,
            payload.client_name,
            payload.company_id,
            payload.engineer_user_id,
            payload.address,
            payload.number,
            payload.district,
            payload.city,
            payload.state,
            payload.zipcode,
            payload.latitude,
            payload.longitude,
            payload.budget_amount,
            payload.start_date,
            payload.end_date,
            payload.status,
        )
        if project_rs.error:
            result.make_error(0, 'Erro ao criar obra inicial', project_rs.message)
            return result.toJSON()

        project_id = project_rs.dataset.recordset[0]['id']

        team_rs = tenant.xp_nx.FDXQuery(
            SQL_TEAM_INSERT,
            project_id,
            payload.main_team_name,
            payload.main_team_description,
            True,
        )
        if team_rs.error:
            result.make_error(0, 'Erro ao criar equipe principal', team_rs.message)
            return result.toJSON()

        team_id = team_rs.dataset.recordset[0]['id']
        created_members = []

        for member in payload.members or []:
            member_name = member.get('member_name', '')
            role_name = member.get('role_name', '')
            user_id = member.get('user_id')
            active = member.get('active', True)

            member_validation = _validate_team_member_payload(
                tenant,
                TeamMemberInput(
                    team_id=team_id,
                    user_id=user_id,
                    member_name=member_name,
                    role_name=role_name,
                    active=active,
                ),
            )
            if member_validation.error:
                return member_validation.toJSON()

            member_rs = tenant.xp_nx.FDXQuery(
                SQL_TEAM_MEMBER_INSERT,
                team_id,
                user_id,
                member_name,
                role_name,
                active,
            )
            if member_rs.error:
                result.make_error(0, 'Erro ao criar membro inicial da equipe', member_rs.message)
                return result.toJSON()
            created_members.append(member_rs.dataset.recordset[0]['id'])

        auth_payload = opened.data or {}
        write_audit_log(
            tenant,
            None,
            auth_payload.get('auth_payload', {}).get('user_id'),
            'projects',
            'setup',
            'projects',
            project_id,
            request.remote_addr,
            {
                'project_id': project_id,
                'main_team_id': team_id,
                'team_members_ids': created_members,
            },
        )

        result.status = True
        result.message = 'Setup inicial da obra executado com sucesso'
        result.data = {
            'project_id': project_id,
            'main_team_id': team_id,
            'team_members_ids': created_members,
        }
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/daily/occurrences', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_occurrences():
    return _crud_resource(
        'diary.read',
        'diary.write',
        SQL_DAILY_OCCURRENCES_LIST,
        SQL_DAILY_OCCURRENCE_INSERT,
        SQL_DAILY_OCCURRENCE_UPDATE,
        SQL_DAILY_OCCURRENCE_DELETE,
        DailyOccurrenceInput,
        lambda p: [p.daily_log_id, p.occurrence_type, p.title, p.description, p.severity, p.resolved],
        lambda p: [p.occurrence_type, p.title, p.description, p.severity, p.resolved, p.id],
        'daily_log_id',
        SQL_DAILY_OCCURRENCE_BY_ID,
        'diary',
        'daily_log_occurrences',
    )


@app.route('/api/v1/daily/activities', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_activities():
    return _crud_resource(
        'diary.read',
        'diary.write',
        SQL_DAILY_ACTIVITIES_LIST,
        SQL_DAILY_ACTIVITY_INSERT,
        SQL_DAILY_ACTIVITY_UPDATE,
        SQL_DAILY_ACTIVITY_DELETE,
        DailyActivityInput,
        lambda p: [p.daily_log_id, p.service_name, p.quantity, p.unit, p.location, p.notes],
        lambda p: [p.service_name, p.quantity, p.unit, p.location, p.notes, p.id],
        'daily_log_id',
        SQL_DAILY_ACTIVITY_BY_ID,
        'diary',
        'daily_log_activities',
    )


@app.route('/api/v1/daily/labor', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_labor():
    return _crud_resource(
        'diary.read',
        'diary.write',
        SQL_DAILY_LABOR_LIST,
        SQL_DAILY_LABOR_INSERT,
        SQL_DAILY_LABOR_UPDATE,
        SQL_DAILY_LABOR_DELETE,
        DailyLaborInput,
        lambda p: [p.daily_log_id, p.team_member_id, p.worker_name, p.role_name, p.hours_worked, p.present],
        lambda p: [p.team_member_id, p.worker_name, p.role_name, p.hours_worked, p.present, p.id],
        'daily_log_id',
        SQL_DAILY_LABOR_BY_ID,
        'diary',
        'daily_log_labor',
    )


@app.route('/api/v1/daily/materials', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_materials():
    return _crud_resource(
        'diary.read',
        'diary.write',
        SQL_DAILY_MATERIALS_LIST,
        SQL_DAILY_MATERIAL_INSERT,
        SQL_DAILY_MATERIAL_UPDATE,
        SQL_DAILY_MATERIAL_DELETE,
        DailyMaterialInput,
        lambda p: [p.daily_log_id, p.material_name, p.movement_type, p.quantity, p.unit, p.notes],
        lambda p: [p.material_name, p.movement_type, p.quantity, p.unit, p.notes, p.id],
        'daily_log_id',
        SQL_DAILY_MATERIAL_BY_ID,
        'diary',
        'daily_log_materials',
    )


@app.route('/api/v1/daily/equipments', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_equipments():
    return _crud_resource(
        'diary.read',
        'diary.write',
        SQL_DAILY_EQUIPMENTS_LIST,
        SQL_DAILY_EQUIPMENT_INSERT,
        SQL_DAILY_EQUIPMENT_UPDATE,
        SQL_DAILY_EQUIPMENT_DELETE,
        DailyEquipmentInput,
        lambda p: [p.daily_log_id, p.equipment_name, p.status, p.hours_used, p.notes],
        lambda p: [p.equipment_name, p.status, p.hours_used, p.notes, p.id],
        'daily_log_id',
        SQL_DAILY_EQUIPMENT_BY_ID,
        'diary',
        'daily_log_equipments',
    )


@app.route('/api/v1/daily/files', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_files():
    return _crud_resource(
        'diary.read',
        'diary.write',
        SQL_DAILY_FILES_LIST,
        SQL_DAILY_FILE_INSERT,
        SQL_DAILY_FILE_UPDATE,
        SQL_DAILY_FILE_DELETE,
        DailyFileInput,
        lambda p: [p.daily_log_id, p.file_name, p.file_type, p.file_url, p.file_size_bytes, p.notes],
        lambda p: [p.file_name, p.file_type, p.file_url, p.file_size_bytes, p.notes, p.id],
        'daily_log_id',
        SQL_DAILY_FILE_BY_ID,
        'diary',
        'daily_log_files',
    )


@app.route('/api/v1/daily/signatures', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_signatures():
    return _crud_resource(
        'diary.read',
        'diary.write',
        SQL_DAILY_SIGNATURES_LIST,
        SQL_DAILY_SIGNATURE_INSERT,
        SQL_DAILY_SIGNATURE_UPDATE,
        SQL_DAILY_SIGNATURE_DELETE,
        DailySignatureInput,
        lambda p: [p.daily_log_id, p.signed_by_user_id, p.signer_name, p.signature_type, p.signature_data],
        lambda p: [p.signed_by_user_id, p.signer_name, p.signature_type, p.signature_data, p.id],
        'daily_log_id',
        SQL_DAILY_SIGNATURE_BY_ID,
        'diary',
        'daily_log_signatures',
    )

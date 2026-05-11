from flask import request

from source.app import app
from source.core.system.core import *
from source.logic.orb_operational import *


def _operational_permissions(method, resource_name):
    resource_permissions = {
        'dashboard': {
            'GET': ('dashboard.read',),
        },
        'projects': {
            'GET': ('projects.read',),
            'POST': ('projects.write',),
            'PUT': ('projects.write',),
            'DELETE': ('projects.write',),
        },
        'teams': {
            'GET': ('teams.read',),
            'POST': ('teams.write',),
            'PUT': ('teams.write',),
            'DELETE': ('teams.write',),
        },
        'team_members': {
            'GET': ('teams.read',),
            'POST': ('teams.write',),
            'PUT': ('teams.write',),
            'DELETE': ('teams.write',),
        },
        'reports': {
            'GET': ('reports.read',),
        },
        'project_setup': {
            'POST': ('projects.write', 'teams.write'),
        },
        'daily_resources': {
            'GET': ('diary.read',),
            'POST': ('diary.write',),
            'PUT': ('diary.write',),
            'DELETE': ('diary.write',),
        },
    }
    return resource_permissions.get(resource_name, {}).get(method, ())


def _authorize_operational(nx, method, resource_name):
    permission_codes = _operational_permissions(method, resource_name)
    if resource_name == 'project_setup':
        return require_tenant_permissions_all(nx, *permission_codes)
    return require_tenant_permissions(nx, *permission_codes)


def _run_tenant_action(token_id, resource_name, get_action=None, post_action=None, put_action=None, delete_action=None, error_message='Erro ao processar operacao'):
    r = NXResult()
    data = request.get_json(silent=True)

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.SYSTEM, token_id)

        if r.status is True:
            permission_result = _authorize_operational(nx, request.method, resource_name)
            if permission_result.error:
                return permission_result.toJSON()
            if request.method == 'GET' and get_action:
                r = get_action(nx, request.args.to_dict())
            elif request.method == 'POST' and post_action:
                if data:
                    r = post_action(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'PUT' and put_action:
                if data:
                    r = put_action(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'DELETE' and delete_action:
                r = delete_action(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, error_message, str(e))

    return r.toJSON()


@app.route('/api/v1/dashboard/operational/<token_id>', methods=['GET'])
def dashboard_operational(token_id):
    return _run_tenant_action(
        token_id,
        'dashboard',
        get_action=lambda nx, _data: dashboard_operational_get(nx),
        error_message='Erro ao montar dashboard operacional',
    )


@app.route('/api/v1/projects/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def projects(token_id):
    return _run_tenant_action(
        token_id,
        'projects',
        get_action=lambda nx, _data: projects_list(nx),
        post_action=projects_create,
        put_action=projects_update,
        delete_action=projects_delete,
        error_message='Erro ao processar obras',
    )


@app.route('/api/v1/teams/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def teams(token_id):
    return _run_tenant_action(
        token_id,
        'teams',
        get_action=teams_list,
        post_action=teams_create,
        put_action=teams_update,
        delete_action=teams_delete,
        error_message='Erro ao processar equipes',
    )


@app.route('/api/v1/team_members/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def team_members(token_id):
    return _run_tenant_action(
        token_id,
        'team_members',
        get_action=team_members_list,
        post_action=team_members_create,
        put_action=team_members_update,
        delete_action=team_members_delete,
        error_message='Erro ao processar membros da equipe',
    )


@app.route('/api/v1/reports/project-diaries/<token_id>', methods=['GET'])
@app.route('/api/v1/reports/projects/diaries/<token_id>', methods=['GET'])
def report_project_diaries(token_id):
    return _run_tenant_action(
        token_id,
        'reports',
        get_action=report_project_diaries_get,
        error_message='Erro ao montar relatorio por obra',
    )


@app.route('/api/v1/reports/project-summary/<token_id>', methods=['GET'])
@app.route('/api/v1/reports/projects/summary/<token_id>', methods=['GET'])
def report_project_summary(token_id):
    return _run_tenant_action(
        token_id,
        'reports',
        get_action=report_project_summary_get,
        error_message='Erro ao montar resumo operacional por obra',
    )


@app.route('/api/v1/projects/setup/<token_id>', methods=['POST'])
def project_setup(token_id):
    return _run_tenant_action(
        token_id,
        'project_setup',
        post_action=project_setup_create,
        error_message='Erro ao executar setup inicial da obra',
    )


@app.route('/api/v1/daily/occurrences/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_occurrences(token_id):
    return _run_tenant_action(
        token_id,
        'daily_resources',
        get_action=daily_occurrences_list,
        post_action=daily_occurrences_create,
        put_action=daily_occurrences_update,
        delete_action=daily_occurrences_delete,
        error_message='Erro ao processar ocorrencias do diario',
    )


@app.route('/api/v1/daily/activities/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_activities(token_id):
    return _run_tenant_action(
        token_id,
        'daily_resources',
        get_action=daily_activities_list,
        post_action=daily_activities_create,
        put_action=daily_activities_update,
        delete_action=daily_activities_delete,
        error_message='Erro ao processar atividades do diario',
    )


@app.route('/api/v1/daily/labor/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_labor(token_id):
    return _run_tenant_action(
        token_id,
        'daily_resources',
        get_action=daily_labor_list,
        post_action=daily_labor_create,
        put_action=daily_labor_update,
        delete_action=daily_labor_delete,
        error_message='Erro ao processar mao de obra do diario',
    )


@app.route('/api/v1/daily/materials/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_materials(token_id):
    return _run_tenant_action(
        token_id,
        'daily_resources',
        get_action=daily_materials_list,
        post_action=daily_materials_create,
        put_action=daily_materials_update,
        delete_action=daily_materials_delete,
        error_message='Erro ao processar materiais do diario',
    )


@app.route('/api/v1/daily/equipments/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_equipments(token_id):
    return _run_tenant_action(
        token_id,
        'daily_resources',
        get_action=daily_equipments_list,
        post_action=daily_equipments_create,
        put_action=daily_equipments_update,
        delete_action=daily_equipments_delete,
        error_message='Erro ao processar equipamentos do diario',
    )


@app.route('/api/v1/daily/files/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_files(token_id):
    return _run_tenant_action(
        token_id,
        'daily_resources',
        get_action=daily_files_list,
        post_action=daily_files_create,
        put_action=daily_files_update,
        delete_action=daily_files_delete,
        error_message='Erro ao processar arquivos do diario',
    )


@app.route('/api/v1/daily/signatures/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def daily_signatures(token_id):
    return _run_tenant_action(
        token_id,
        'daily_resources',
        get_action=daily_signatures_list,
        post_action=daily_signatures_create,
        put_action=daily_signatures_update,
        delete_action=daily_signatures_delete,
        error_message='Erro ao processar assinaturas do diario',
    )

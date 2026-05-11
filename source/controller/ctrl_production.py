from flask import request
from source.app import app
from source.logic.orb_production import *
from source.core.system.core import *


def _production_permissions(method, resource_name):
    resource_permissions = {
        'production': {
            'GET': ('production.read',),
            'POST': ('production.write',),
            'PUT': ('production.write',),
            'DELETE': ('production.write',),
        },
        'audit': {
            'GET': ('audit.read',),
        },
        'dashboard': {
            'GET': ('dashboard.read',),
        },
        'indicators': {
            'GET': ('dashboard.read', 'reports.read'),
        },
    }
    return resource_permissions.get(resource_name, {}).get(method, ())


def _login_and_authorize(token_id, resource_name):
    nx = NXConnection()
    result = nx.login(NXLoginType.SYSTEM, token_id)
    if result.status is True:
        result = require_tenant_permissions(nx, *_production_permissions(request.method, resource_name))
    return nx, result


@app.route('/api/v1/production/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def production_index(token_id):
    r = NXResult()
    data = request.get_json(silent=True)

    try:
        nx, r = _login_and_authorize(token_id, 'production')

        if r.status is True:
            if request.method == 'GET':
                r = production_list(nx, request.args.to_dict())
            elif request.method == 'POST':
                if data:
                    r = production_create(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'PUT':
                if data:
                    r = production_update(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'DELETE':
                r = production_delete(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, 'Erro ao processar producao', str(e))

    return r.toJSON()


@app.route('/api/v1/audit/logs/<token_id>', methods=['GET'])
def audit_logs(token_id):
    r = NXResult()
    try:
        nx, r = _login_and_authorize(token_id, 'audit')
        if r.status is True:
            r = audit_logs_list(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, 'Erro ao consultar auditoria', str(e))

    return r.toJSON()


@app.route('/api/v1/audit/summary/<token_id>', methods=['GET'])
def audit_summary(token_id):
    r = NXResult()
    try:
        nx, r = _login_and_authorize(token_id, 'audit')
        if r.status is True:
            r = audit_summary_list(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, 'Erro ao consultar resumo de auditoria', str(e))

    return r.toJSON()


@app.route('/api/v1/audit/timeline/project/<token_id>', methods=['GET'])
@app.route('/api/v1/audit/projects/timeline/<token_id>', methods=['GET'])
def audit_timeline_project(token_id):
    r = NXResult()
    try:
        nx, r = _login_and_authorize(token_id, 'audit')
        if r.status is True:
            r = audit_timeline_project_list(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, 'Erro ao consultar timeline da obra', str(e))

    return r.toJSON()


@app.route('/api/v1/audit/timeline/diary/<token_id>', methods=['GET'])
@app.route('/api/v1/audit/diaries/timeline/<token_id>', methods=['GET'])
def audit_timeline_diary(token_id):
    r = NXResult()
    try:
        nx, r = _login_and_authorize(token_id, 'audit')
        if r.status is True:
            r = audit_timeline_diary_list(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, 'Erro ao consultar timeline do diario', str(e))

    return r.toJSON()


@app.route('/api/v1/dashboard/user-summary/<token_id>', methods=['GET'])
@app.route('/api/v1/dashboard/users/summary/<token_id>', methods=['GET'])
def dashboard_user_summary(token_id):
    r = NXResult()
    try:
        nx, r = _login_and_authorize(token_id, 'dashboard')
        if r.status is True:
            r = dashboard_summary_by_user(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, 'Erro ao montar dashboard por responsavel', str(e))

    return r.toJSON()


@app.route('/api/v1/indicators/diary/by-user/<token_id>', methods=['GET'])
def indicator_diary_by_user(token_id):
    r = NXResult()
    try:
        nx, r = _login_and_authorize(token_id, 'indicators')
        if r.status is True:
            r = indicators_diary_by_user(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, 'Erro ao montar indicadores de diario por responsavel', str(e))

    return r.toJSON()


@app.route('/api/v1/indicators/production/by-user/<token_id>', methods=['GET'])
def indicator_production_by_user(token_id):
    r = NXResult()
    try:
        nx, r = _login_and_authorize(token_id, 'indicators')
        if r.status is True:
            r = indicators_production_by_user(nx, request.args.to_dict())
    except Exception as e:
        r.make_error(0, 'Erro ao montar indicadores de producao por responsavel', str(e))

    return r.toJSON()

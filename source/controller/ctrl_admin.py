from flask import request

from source.app import app
from source.core.config.config import appConfig
from source.core.system.core import *
from source.logic.orb_admin import *


def _setup_key_valid() -> bool:
    header_key = request.headers.get('X-Setup-Key', '').strip()
    return bool(appConfig.setupKey) and header_key == appConfig.setupKey


def _request_payload() -> dict:
    payload = request.get_json(silent=True)
    if payload:
        return payload
    return request.args.to_dict()


@app.route('/api/v1/admin/accounts/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_accounts(token_id):
    r = NXResult()
    data = _request_payload()

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.ORB, token_id)

        if r.status is True:
            if request.method == 'GET':
                r = admin_accounts_list(nx, data)
            elif request.method == 'POST':
                if data:
                    r = admin_accounts_create(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'PUT':
                if data:
                    r = admin_accounts_update(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'DELETE':
                if data:
                    r = admin_accounts_delete(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
    except Exception as e:
        r.make_error(0, 'Erro ao processar contas administrativas', str(e))

    return r.toJSON()


@app.route('/api/v1/admin/plans/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_plans(token_id):
    r = NXResult()
    data = _request_payload()

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.ORB, token_id)

        if r.status is True:
            if request.method == 'GET':
                r = admin_plans_list(nx, data)
            elif request.method == 'POST':
                if data:
                    r = admin_plans_create(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'PUT':
                if data:
                    r = admin_plans_update(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'DELETE':
                if data:
                    r = admin_plans_delete(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
    except Exception as e:
        r.make_error(0, 'Erro ao processar planos administrativos', str(e))

    return r.toJSON()


@app.route('/api/v1/admin/modules/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_modules(token_id):
    r = NXResult()
    data = _request_payload()

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.ORB, token_id)

        if r.status is True:
            if request.method == 'GET':
                r = admin_modules_list(nx, data)
            elif request.method == 'POST':
                if data:
                    r = admin_modules_create(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'PUT':
                if data:
                    r = admin_modules_update(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'DELETE':
                if data:
                    r = admin_modules_delete(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
    except Exception as e:
        r.make_error(0, 'Erro ao processar modulos administrativos', str(e))

    return r.toJSON()


@app.route('/api/v1/admin/account_modules/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_account_modules(token_id):
    r = NXResult()
    data = _request_payload()

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.ORB, token_id)

        if r.status is True:
            if request.method == 'GET':
                r = admin_account_modules_list(nx, data)
            elif request.method == 'POST':
                if data:
                    r = admin_account_modules_create(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'PUT':
                if data:
                    r = admin_account_modules_update(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'DELETE':
                if data:
                    r = admin_account_modules_delete(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
    except Exception as e:
        r.make_error(0, 'Erro ao processar modulos por conta', str(e))

    return r.toJSON()


@app.route('/api/v1/admin/master_users/<token_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_master_users(token_id):
    r = NXResult()
    data = _request_payload()

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.ORB, token_id)

        if r.status is True:
            if request.method == 'GET':
                r = admin_master_users_list(nx, data)
            elif request.method == 'POST':
                if data:
                    r = admin_master_users_create(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'PUT':
                if data:
                    r = admin_master_users_update(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'DELETE':
                if data:
                    r = admin_master_users_delete(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
    except Exception as e:
        r.make_error(0, 'Erro ao processar usuarios master', str(e))

    return r.toJSON()


@app.route('/api/v1/admin/bootstrap/<token_id>', methods=['GET', 'POST'])
def admin_bootstrap(token_id):
    r = NXResult()
    data = request.get_json(silent=True)

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.ORB, token_id)

        if r.status is True:
            if request.method == 'GET':
                r = admin_bootstrap_status(nx)
            elif request.method == 'POST':
                r = admin_bootstrap_master(nx, data or {})
    except Exception as e:
        r.make_error(0, 'Erro ao processar bootstrap administrativo', str(e))

    return r.toJSON()


@app.route('/api/v1/admin/schema-compatibility/<token_id>', methods=['GET'])
def admin_schema_compatibility_route(token_id):
    r = NXResult()

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.ORB, token_id)

        if r.status is True:
            r = admin_schema_compatibility(nx)
    except Exception as e:
        r.make_error(0, 'Erro ao processar compatibilidade de schema', str(e))

    return r.toJSON()


@app.route('/api/v1/admin/migrations/<token_id>', methods=['GET', 'POST'])
def admin_migrations_route(token_id):
    r = NXResult()

    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.ORB, token_id)

        if r.status is True:
            if request.method == 'GET':
                r = admin_migrations_status(nx)
            elif request.method == 'POST':
                r = admin_migrations_apply(nx)
    except Exception as e:
        r.make_error(0, 'Erro ao processar migrations administrativas', str(e))

    return r.toJSON()


@app.route('/api/v1/setup/status', methods=['GET'])
def public_setup_status_route():
    r = NXResult()
    if not _setup_key_valid():
        r.make_error(403, 'Chave de setup invalida')
        return r.toJSON()

    nx = NXMasterConnection()
    try:
        r = nx.active()
        if r.status is True:
            r = public_setup_status(nx)
    except Exception as e:
        r.make_error(0, 'Erro ao consultar status de setup inicial', str(e))
    finally:
        nx.stop()

    return r.toJSON()


@app.route('/api/v1/setup/initialize', methods=['POST'])
def public_setup_initialize_route():
    r = NXResult()
    data = request.get_json(silent=True) or {}
    if not _setup_key_valid():
        r.make_error(403, 'Chave de setup invalida')
        return r.toJSON()

    nx = NXMasterConnection()
    try:
        r = nx.active()
        if r.status is True:
            r = public_setup_initialize(nx, data)
    except Exception as e:
        r.make_error(0, 'Erro ao executar setup inicial', str(e))
    finally:
        nx.stop()

    return r.toJSON()

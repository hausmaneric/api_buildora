from source.app import app
from source.logic.orb_tenant import *
from source.core.system.core import *


def _tenant_permissions(method, resource_name):
    resource_permissions = {
        'metadata': {
            'GET': ('companies.read', 'users.read', 'roles.read', 'permissions.read'),
        },
        'companies': {
            'GET': ('companies.read',),
            'POST': ('companies.write',),
        },
        'roles': {
            'GET': ('roles.read',),
            'POST': ('roles.write',),
        },
        'permissions': {
            'GET': ('permissions.read',),
            'POST': ('permissions.write',),
        },
        'role_permissions': {
            'GET': ('roles.permissions.read',),
            'POST': ('roles.permissions.write',),
        },
        'users': {
            'GET': ('users.read',),
            'POST': ('users.write',),
        },
        'bootstrap': {
            'POST': ('companies.write', 'users.write', 'roles.write', 'permissions.write', 'roles.permissions.write'),
        },
    }
    return resource_permissions.get(resource_name, {}).get(method, ())


def _authorize_tenant_resource(nx, method, resource_name):
    permission_codes = _tenant_permissions(method, resource_name)
    if resource_name in {'metadata', 'bootstrap'}:
        return require_tenant_permissions_all(nx, *permission_codes)
    return require_tenant_permissions(nx, *permission_codes)


@app.route('/api/v1/tenant/metadata/<token_id>', methods=['GET'])
def tenant_metadata(token_id):
    r = NXResult()
    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.SYSTEM, token_id)
        if r.status is True:
            r = _authorize_tenant_resource(nx, request.method, 'metadata')
        if r.status is True:
            r = tenant_metadata_get(nx)
    except Exception as e:
        r.make_error(0, 'Erro ao consultar metadados do ambiente', str(e))

    return r.toJSON()


def _run_tenant_action(token_id, resource_name, get_action=None, post_action=None, error_message='Erro ao processar ambiente tenant'):
    r = NXResult()
    data = request.get_json(silent=True)
    try:
        nx = NXConnection()
        r = nx.login(NXLoginType.SYSTEM, token_id)
        if r.status is True:
            r = _authorize_tenant_resource(nx, request.method, resource_name)
        if r.status is True:
            if request.method == 'GET' and get_action:
                r = get_action(nx)
            elif request.method == 'POST' and post_action:
                if data:
                    r = post_action(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
    except Exception as e:
        r.make_error(0, error_message, str(e))

    return r.toJSON()


@app.route('/api/v1/tenant/companies/<token_id>', methods=['GET', 'POST'])
def tenant_companies(token_id):
    return _run_tenant_action(
        token_id,
        'companies',
        get_action=tenant_companies_list,
        post_action=tenant_companies_create,
        error_message='Erro ao processar empresas do ambiente',
    )


@app.route('/api/v1/tenant/roles/<token_id>', methods=['GET', 'POST'])
def tenant_roles(token_id):
    return _run_tenant_action(
        token_id,
        'roles',
        get_action=tenant_roles_list,
        post_action=tenant_roles_create,
        error_message='Erro ao processar perfis do ambiente',
    )


@app.route('/api/v1/tenant/permissions/<token_id>', methods=['GET', 'POST'])
def tenant_permissions(token_id):
    return _run_tenant_action(
        token_id,
        'permissions',
        get_action=tenant_permissions_list,
        post_action=tenant_permissions_create,
        error_message='Erro ao processar permissoes do ambiente',
    )


@app.route('/api/v1/tenant/role_permissions/<token_id>', methods=['GET', 'POST'])
def tenant_role_permissions(token_id):
    return _run_tenant_action(
        token_id,
        'role_permissions',
        get_action=tenant_role_permissions_list,
        post_action=tenant_role_permissions_create,
        error_message='Erro ao processar vinculos de permissao',
    )


@app.route('/api/v1/tenant/users/<token_id>', methods=['GET', 'POST'])
def tenant_users(token_id):
    return _run_tenant_action(
        token_id,
        'users',
        get_action=tenant_users_list,
        post_action=tenant_users_create,
        error_message='Erro ao processar usuarios do ambiente',
    )


@app.route('/api/v1/tenant/bootstrap/<token_id>', methods=['POST'])
def tenant_bootstrap(token_id):
    return _run_tenant_action(
        token_id,
        'bootstrap',
        post_action=tenant_bootstrap_create,
        error_message='Erro ao executar bootstrap do ambiente',
    )

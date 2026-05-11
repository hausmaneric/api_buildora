from flask import request
from classes.next_base import NXResult
from classes.obrax_utils import (
    NXMasterConnection,
    NXTenantConnection,
    decode_token,
    generate_token,
    hash_password,
    write_audit_log,
)
from classes.sql.obx_sql import (
    SQL_ACCOUNT_BY_CODE,
    SQL_MASTER_LOGIN,
    SQL_TENANT_LOGIN,
    SQL_TENANT_ROLE_PERMISSIONS_BY_USER,
)


def bearer_token() -> str:
    return request.headers.get('Authorization', '').replace('Bearer ', '').strip()


def resolve_account_by_code(account_code: str) -> tuple[NXResult, dict | None]:
    result = NXResult()
    if not account_code:
        result.make_error(0, 'Cabeçalho X-Account-Code é obrigatório')
        return result, None

    master = NXMasterConnection()
    opened = master.active()
    if opened.error:
        return opened, None

    try:
        rs = master.xp_nx.FDXQuery(SQL_ACCOUNT_BY_CODE, account_code)
        if rs.error:
            result.make_error(0, 'Erro ao localizar ambiente', rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, 'Ambiente não localizado')
            return result, None
        ok = NXResult()
        ok.status = True
        return ok, rs.dataset.recordset[0]
    finally:
        master.stop()


def open_tenant_connection(account_code: str) -> tuple[NXResult, NXTenantConnection | None, dict | None]:
    resolved, account = resolve_account_by_code(account_code)
    if resolved.error:
        return resolved, None, None

    tenant = NXTenantConnection()
    opened = tenant.active_by_account(account)
    if opened.error:
        return opened, None, None

    ok = NXResult()
    ok.status = True
    return ok, tenant, account


def authenticate_master(login: str, password: str) -> NXResult:
    result = NXResult()
    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened

    try:
        rs = nx.xp_nx.FDXQuery(SQL_MASTER_LOGIN, login)
        if rs.error:
            result.make_error(0, 'Erro ao consultar usuário master', rs.message)
        elif rs.dataset.recordcount == 0:
            write_audit_log(
                nx,
                None,
                None,
                'auth',
                'master_login_failed',
                'master_users',
                None,
                request.remote_addr,
                {'login': login},
            )
            result.make_error(0, 'Usuário master não localizado')
        else:
            user = rs.dataset.recordset[0]
            if not user.get('active', True):
                write_audit_log(
                    nx,
                    None,
                    user.get('id'),
                    'auth',
                    'master_login_failed',
                    'master_users',
                    user.get('id'),
                    request.remote_addr,
                    {'login': login, 'reason': 'inactive'},
                )
                result.make_error(0, 'Usuário master inativo')
            elif user.get('password_hash') != hash_password(password):
                write_audit_log(
                    nx,
                    None,
                    user.get('id'),
                    'auth',
                    'master_login_failed',
                    'master_users',
                    user.get('id'),
                    request.remote_addr,
                    {'login': login, 'reason': 'invalid_password'},
                )
                result.make_error(0, 'Usuário e senha incorretos')
            else:
                write_audit_log(
                    nx,
                    None,
                    user.get('id'),
                    'auth',
                    'master_login',
                    'master_users',
                    user.get('id'),
                    request.remote_addr,
                    {'login': login},
                )
                result.status = True
                result.data = {
                    'token': generate_token({
                        'user_id': user['id'],
                        'scope': 'master',
                        'login': user['login'],
                        'role': user.get('role', 'admin'),
                    }),
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'login': user['login'],
                        'email': user.get('email'),
                        'role': user.get('role', 'admin'),
                    },
                }
                result.message = 'Login master realizado com sucesso'
    finally:
        nx.stop()

    return result


def authenticate_tenant(account_code: str, email: str, password: str) -> NXResult:
    result, tenant, account = open_tenant_connection(account_code)
    if result.error:
        return result

    auth = NXResult()
    try:
        rs = tenant.xp_nx.FDXQuery(SQL_TENANT_LOGIN, email)
        if rs.error:
            auth.make_error(0, 'Erro ao consultar usuário do ambiente', rs.message)
        elif rs.dataset.recordcount == 0:
            write_audit_log(
                tenant,
                account.get('id'),
                None,
                'auth',
                'tenant_login_failed',
                'users',
                None,
                request.remote_addr,
                {'account_code': account_code, 'email': email},
            )
            auth.make_error(0, 'Usuário do ambiente não localizado')
        else:
            user = rs.dataset.recordset[0]
            if not user.get('active', True):
                write_audit_log(
                    tenant,
                    account.get('id'),
                    user.get('id'),
                    'auth',
                    'tenant_login_failed',
                    'users',
                    user.get('id'),
                    request.remote_addr,
                    {'account_code': account_code, 'email': email, 'reason': 'inactive'},
                )
                auth.make_error(0, 'Usuário do ambiente inativo')
            elif user.get('password_hash') != hash_password(password):
                write_audit_log(
                    tenant,
                    account.get('id'),
                    user.get('id'),
                    'auth',
                    'tenant_login_failed',
                    'users',
                    user.get('id'),
                    request.remote_addr,
                    {'account_code': account_code, 'email': email, 'reason': 'invalid_password'},
                )
                auth.make_error(0, 'Usuário e senha incorretos')
            else:
                permissions_rs = tenant.xp_nx.FDXQuery(SQL_TENANT_ROLE_PERMISSIONS_BY_USER, user['id'])
                permissions = []
                if not permissions_rs.error:
                    permissions = [row['code'] for row in permissions_rs.dataset.recordset if row.get('code')]
                write_audit_log(
                    tenant,
                    account.get('id'),
                    user.get('id'),
                    'auth',
                    'tenant_login',
                    'users',
                    user.get('id'),
                    request.remote_addr,
                    {'account_code': account_code, 'email': email},
                )
                auth.status = True
                auth.message = 'Login do ambiente realizado com sucesso'
                auth.data = {
                    'token': generate_token({
                        'user_id': user['id'],
                        'scope': 'tenant',
                        'account_code': account['code'],
                        'email': user['email'],
                        'role': user.get('role', 'user'),
                        'role_id': user.get('role_id'),
                        'permissions': permissions,
                    }),
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email'],
                        'role': user.get('role', 'user'),
                        'role_id': user.get('role_id'),
                        'company_id': user.get('company_id'),
                        'permissions': permissions,
                    },
                    'account': {
                        'id': account['id'],
                        'code': account['code'],
                        'name': account['name'],
                    },
                }
    finally:
        tenant.stop()

    return auth


def require_scope(expected_scope: str) -> tuple[NXResult, dict | None]:
    result = NXResult()
    token = bearer_token()
    if not token:
        result.make_error(401, 'Token não informado')
        return result, None

    try:
        payload = decode_token(token)
        if payload.get('scope') != expected_scope:
            result.make_error(403, 'Escopo de acesso inválido')
            return result, None
        ok = NXResult()
        ok.status = True
        return ok, payload
    except Exception as e:
        result.make_error(401, 'Token inválido', str(e))
        return result, None


def require_tenant_permission(permission_code: str) -> tuple[NXResult, dict | None]:
    result, payload = require_scope('tenant')
    if result.error:
        return result, None

    permissions = payload.get('permissions', []) or []
    if permission_code not in permissions:
        denied = NXResult()
        denied.make_error(403, f'Permissão obrigatória não concedida: {permission_code}')
        return denied, None

    ok = NXResult()
    ok.status = True
    return ok, payload

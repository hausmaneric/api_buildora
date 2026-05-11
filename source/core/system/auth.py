from flask import request

from source.core.system.database import NXMasterConnection, NXTenantConnection
from source.core.system.security import hash_password, write_audit_log
from source.core.system.utils import NXResult, decode_token, encode_token
from source.data.sql.sql_obrax import (
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
        result.make_error(0, 'Cabecalho X-Account-Code e obrigatorio')
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
            result.make_error(0, 'Ambiente nao localizado')
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
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
            result.make_error(0, 'Erro ao consultar usuario master', rs.message)
        elif rs.dataset.recordcount == 0:
            write_audit_log(nx, None, None, 'auth', 'master_login_failed', 'master_users', None, request.remote_addr, {'login': login})
            result.make_error(0, 'Usuario master nao localizado')
        else:
            user = rs.dataset.recordset[0]
            if not user.get('active', True):
                write_audit_log(nx, None, user.get('id'), 'auth', 'master_login_failed', 'master_users', user.get('id'), request.remote_addr, {'login': login, 'reason': 'inactive'})
                result.make_error(0, 'Usuario master inativo')
            elif user.get('password_hash') != hash_password(password):
                write_audit_log(nx, None, user.get('id'), 'auth', 'master_login_failed', 'master_users', user.get('id'), request.remote_addr, {'login': login, 'reason': 'invalid_password'})
                result.make_error(0, 'Usuario e senha incorretos')
            else:
                write_audit_log(nx, None, user.get('id'), 'auth', 'master_login', 'master_users', user.get('id'), request.remote_addr, {'login': login})
                result.status = True
                result.message = 'Login master realizado com sucesso'
                result.data = {
                    'token': encode_token({
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
            auth.make_error(0, 'Erro ao consultar usuario do ambiente', rs.message)
        elif rs.dataset.recordcount == 0:
            write_audit_log(tenant, account.get('id'), None, 'auth', 'tenant_login_failed', 'users', None, request.remote_addr, {'account_code': account_code, 'email': email})
            auth.make_error(0, 'Usuario do ambiente nao localizado')
        else:
            user = rs.dataset.recordset[0]
            if not user.get('active', True):
                write_audit_log(tenant, account.get('id'), user.get('id'), 'auth', 'tenant_login_failed', 'users', user.get('id'), request.remote_addr, {'account_code': account_code, 'email': email, 'reason': 'inactive'})
                auth.make_error(0, 'Usuario do ambiente inativo')
            elif user.get('password_hash') != hash_password(password):
                write_audit_log(tenant, account.get('id'), user.get('id'), 'auth', 'tenant_login_failed', 'users', user.get('id'), request.remote_addr, {'account_code': account_code, 'email': email, 'reason': 'invalid_password'})
                auth.make_error(0, 'Usuario e senha incorretos')
            else:
                permissions_rs = tenant.xp_nx.FDXQuery(SQL_TENANT_ROLE_PERMISSIONS_BY_USER, user['id'])
                permissions = []
                if not permissions_rs.error:
                    permissions = [row['code'] for row in permissions_rs.dataset.recordset if row.get('code')]

                write_audit_log(tenant, account.get('id'), user.get('id'), 'auth', 'tenant_login', 'users', user.get('id'), request.remote_addr, {'account_code': account_code, 'email': email})
                auth.status = True
                auth.message = 'Login do ambiente realizado com sucesso'
                auth.data = {
                    'token': encode_token({
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
        result.make_error(401, 'Token nao informado')
        return result, None

    try:
        payload = decode_token(token)
        if payload.get('scope') != expected_scope:
            result.make_error(403, 'Escopo de acesso invalido')
            return result, None
        ok = NXResult()
        ok.status = True
        return ok, payload
    except Exception as e:
        result.make_error(401, 'Token invalido', str(e))
        return result, None


def require_tenant_permission(permission_code: str) -> tuple[NXResult, dict | None]:
    result, payload = require_scope('tenant')
    if result.error:
        return result, None

    permissions = payload.get('permissions', []) or []
    if permission_code not in permissions:
        denied = NXResult()
        denied.make_error(403, f'Permissao obrigatoria nao concedida: {permission_code}')
        return denied, None

    ok = NXResult()
    ok.status = True
    return ok, payload

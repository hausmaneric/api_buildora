from flask import request
from app import app
from classes.auth_utils import require_scope
from classes.next_base import NXResult
from classes.obrax_utils import NXMasterConnection, hash_password, write_audit_log
from classes.sql.obx_sql import (
    SQL_ACCOUNT_MODULE_INSERT,
    SQL_ACCOUNT_MODULES_LIST,
    SQL_MASTER_ACCOUNT_INSERT,
    SQL_MASTER_ACCOUNTS_LIST,
    SQL_MASTER_MODULE_INSERT,
    SQL_MASTER_MODULES_LIST,
    SQL_MASTER_PLAN_INSERT,
    SQL_MASTER_PLANS_LIST,
    SQL_MASTER_USER_INSERT,
    SQL_MASTER_USERS_LIST,
)
from models.admin import AccountInput, AccountModuleInput, MasterUserInput, ModuleInput, PlanInput


def _ensure_master() -> str | None:
    auth, _payload = require_scope('master')
    if auth.error:
        return auth.toJSON()
    return None


def _master_payload() -> dict | None:
    auth, payload = require_scope('master')
    if auth.error:
        return None
    return payload


def _execute_master_list(sql: str) -> str:
    denied = _ensure_master()
    if denied:
        return denied

    result = NXResult()
    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened.toJSON()

    try:
        rs = nx.xp_nx.FDXQuery(sql)
        if rs.error:
            result.make_error(0, 'Erro ao consultar dados administrativos', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset
    finally:
        nx.stop()

    return result.toJSON()


@app.route('/api/v1/admin/accounts', methods=['GET', 'POST'])
def admin_accounts():
    denied = _ensure_master()
    if denied:
        return denied

    if request.method == 'GET':
        return _execute_master_list(SQL_MASTER_ACCOUNTS_LIST)

    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados inválidos enviados')
        return result.toJSON()

    payload = AccountInput.from_dict(data)
    auth_payload = _master_payload() or {}
    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened.toJSON()

    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_ACCOUNT_INSERT,
            payload.code,
            payload.name,
            payload.document,
            payload.phone,
            payload.email,
            payload.status,
            payload.plan_id,
            payload.database_url,
            payload.database_host,
            payload.database_port,
            payload.database_name,
            payload.database_user,
            payload.database_password,
            payload.database_sslmode,
            payload.storage_limit_mb,
            payload.storage_used_mb,
            payload.expiration_date,
            payload.active,
        )
        if rs.error:
            result.make_error(0, 'Erro ao cadastrar conta', rs.message)
        else:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                nx,
                record.get('id'),
                auth_payload.get('user_id'),
                'admin',
                'post',
                'accounts',
                record.get('id'),
                request.remote_addr,
                data,
            )
            result.status = True
            result.message = 'Conta cadastrada com sucesso'
            result.data = record if record else None
    finally:
        nx.stop()

    return result.toJSON()


@app.route('/api/v1/admin/plans', methods=['GET', 'POST'])
def admin_plans():
    denied = _ensure_master()
    if denied:
        return denied

    if request.method == 'GET':
        return _execute_master_list(SQL_MASTER_PLANS_LIST)

    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados inválidos enviados')
        return result.toJSON()

    payload = PlanInput.from_dict(data)
    auth_payload = _master_payload() or {}
    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened.toJSON()

    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_PLAN_INSERT,
            payload.name,
            payload.description,
            payload.price,
            payload.max_companies,
            payload.max_users,
            payload.max_works,
            payload.max_storage_mb,
            payload.active,
        )
        if rs.error:
            result.make_error(0, 'Erro ao cadastrar plano', rs.message)
        else:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                nx,
                None,
                auth_payload.get('user_id'),
                'admin',
                'post',
                'plans',
                record.get('id'),
                request.remote_addr,
                data,
            )
            result.status = True
            result.message = 'Plano cadastrado com sucesso'
            result.data = record if record else None
    finally:
        nx.stop()

    return result.toJSON()


@app.route('/api/v1/admin/modules', methods=['GET', 'POST'])
def admin_modules():
    denied = _ensure_master()
    if denied:
        return denied

    if request.method == 'GET':
        return _execute_master_list(SQL_MASTER_MODULES_LIST)

    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados inválidos enviados')
        return result.toJSON()

    payload = ModuleInput.from_dict(data)
    auth_payload = _master_payload() or {}
    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened.toJSON()

    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_MODULE_INSERT,
            payload.code,
            payload.name,
            payload.description,
            payload.active,
        )
        if rs.error:
            result.make_error(0, 'Erro ao cadastrar módulo', rs.message)
        else:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                nx,
                None,
                auth_payload.get('user_id'),
                'admin',
                'post',
                'modules',
                record.get('id'),
                request.remote_addr,
                data,
            )
            result.status = True
            result.message = 'Módulo cadastrado com sucesso'
            result.data = record if record else None
    finally:
        nx.stop()

    return result.toJSON()


@app.route('/api/v1/admin/account_modules', methods=['GET', 'POST'])
def admin_account_modules():
    denied = _ensure_master()
    if denied:
        return denied

    if request.method == 'GET':
        return _execute_master_list(SQL_ACCOUNT_MODULES_LIST)

    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados inválidos enviados')
        return result.toJSON()

    payload = AccountModuleInput.from_dict(data)
    auth_payload = _master_payload() or {}
    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened.toJSON()

    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_ACCOUNT_MODULE_INSERT,
            payload.account_id,
            payload.module_id,
            payload.active,
        )
        if rs.error:
            result.make_error(0, 'Erro ao vincular módulo à conta', rs.message)
        else:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                nx,
                payload.account_id,
                auth_payload.get('user_id'),
                'admin',
                'post',
                'account_modules',
                record.get('id'),
                request.remote_addr,
                data,
            )
            result.status = True
            result.message = 'Vínculo de módulo cadastrado com sucesso'
            result.data = record if record else None
    finally:
        nx.stop()

    return result.toJSON()


@app.route('/api/v1/admin/master_users', methods=['GET', 'POST'])
def admin_master_users():
    denied = _ensure_master()
    if denied:
        return denied

    if request.method == 'GET':
        return _execute_master_list(SQL_MASTER_USERS_LIST)

    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados inválidos enviados')
        return result.toJSON()

    payload = MasterUserInput.from_dict(data)
    auth_payload = _master_payload() or {}
    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened.toJSON()

    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_USER_INSERT,
            payload.name,
            payload.login,
            hash_password(payload.password),
            payload.email,
            payload.phone,
            payload.role,
            payload.active,
        )
        if rs.error:
            result.make_error(0, 'Erro ao cadastrar usuário master', rs.message)
        else:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                nx,
                None,
                auth_payload.get('user_id'),
                'admin',
                'post',
                'master_users',
                record.get('id'),
                request.remote_addr,
                {
                    'name': data.get('name'),
                    'login': data.get('login'),
                    'email': data.get('email'),
                    'phone': data.get('phone'),
                    'role': data.get('role'),
                    'active': data.get('active'),
                },
            )
            result.status = True
            result.message = 'Usuário master cadastrado com sucesso'
            result.data = record if record else None
    finally:
        nx.stop()

    return result.toJSON()

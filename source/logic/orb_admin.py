from pathlib import Path
from typing import Any

from source.core.system.database import NXMasterConnection
from source.core.system.security import hash_password, write_audit_log
from source.core.system.utils import NXResult, process_error_message, success_message
from source.data.sql.sql_obrax import (
    SQL_ACCOUNT_MODULE_BY_ID,
    SQL_ACCOUNT_MODULE_BY_ACCOUNT_AND_MODULE,
    SQL_ACCOUNT_MODULES_COUNT,
    SQL_ACCOUNT_MODULE_DELETE,
    SQL_ACCOUNT_MODULE_INSERT,
    SQL_ACCOUNT_MODULES_LIST,
    SQL_ACCOUNT_MODULES_LIST_PAGED,
    SQL_ACCOUNT_MODULE_UPDATE,
    SQL_DATABASE_METADATA_BY_KEY,
    SQL_DATABASE_METADATA_UPSERT,
    SQL_MASTER_ACCOUNT_BY_ID,
    SQL_MASTER_ACCOUNTS_COUNT,
    SQL_MASTER_ACCOUNT_DELETE,
    SQL_MASTER_ACCOUNT_INSERT,
    SQL_MASTER_ACCOUNTS_LIST,
    SQL_MASTER_ACCOUNTS_LIST_PAGED,
    SQL_MASTER_ACCOUNT_UPDATE,
    SQL_MASTER_MODULE_BY_ID,
    SQL_MASTER_MODULE_INSERT,
    SQL_MASTER_MODULE_BY_CODE,
    SQL_MASTER_MODULES_COUNT,
    SQL_MASTER_MODULE_DELETE,
    SQL_MASTER_MODULES_LIST,
    SQL_MASTER_MODULES_LIST_PAGED,
    SQL_MASTER_MODULE_UPDATE,
    SQL_MASTER_PLAN_BY_ID,
    SQL_MASTER_PLAN_INSERT,
    SQL_MASTER_PLANS_COUNT,
    SQL_MASTER_PLAN_DELETE,
    SQL_MASTER_PLAN_BY_NAME,
    SQL_MASTER_PLANS_LIST_PAGED,
    SQL_MASTER_PLAN_UPDATE,
    SQL_TABLE_EXISTS,
    SQL_MASTER_USER_BY_ID,
    SQL_MASTER_USER_BY_LOGIN,
    SQL_MASTER_USERS_COUNT,
    SQL_MASTER_USER_DELETE,
    SQL_MASTER_PLANS_LIST,
    SQL_MASTER_USER_INSERT,
    SQL_MASTER_USERS_LIST_PAGED,
    SQL_MASTER_USERS_LIST,
    SQL_MASTER_USER_UPDATE,
    SQL_MASTER_USER_UPDATE_WITH_PASSWORD,
)


def _master_scope_ok(nx: Any) -> NXResult:
    result = NXResult()
    if nx.session.scope != 'master':
        result.make_error(0, 'Token sem permissao master')
        return result
    result.status = True
    return result


def _master_audit_connection(nx: Any) -> Any:
    return getattr(nx, '_master', nx)


def _session_user_id(nx: Any) -> int:
    session = getattr(nx, 'session', None)
    return getattr(session, 'userid', 0) if session else 0


def _master_users_count(nx: Any) -> tuple[NXResult, int]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_MASTER_USERS_LIST)
        if rs.error:
            if 'does not exist' in (rs.message or '').lower() and 'master_users' in (rs.message or '').lower():
                try:
                    nx.conn_nx.rollback()
                except Exception:
                    pass
                result.status = True
                return result, 0
            try:
                nx.conn_nx.rollback()
            except Exception:
                pass
            result.make_error(0, 'Erro ao consultar usuarios master', rs.message)
            return result, 0
        result.status = True
        return result, rs.dataset.recordcount
    except Exception as e:
        result.make_error(0, 'Erro ao consultar usuarios master', str(e))
        return result, 0


def _list_master(nx: Any, sql: str, error_message: str) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(sql)
        if not rs.error:
            result.status = True
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, error_message, rs.message)
    except Exception as e:
        result.make_error(0, error_message, str(e))
    return result


def _paged_total(nx: Any, sql: str, search_value: str) -> int:
    try:
        like = f'%{search_value}%'
        rs = nx.xp_nx.FDXQuery(sql, search_value, like, like, like, like)
        if rs.error or rs.dataset.recordcount == 0:
            return 0
        return int(rs.dataset.fieldbyname('total', 0) or 0)
    except Exception:
        return 0


def _paged_master(nx: Any, sql: str, count_sql: str | None, search: str, sort_field: str, sort_direction: str, limit: int, offset: int, error_message: str) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        search_value = search.strip()
        like = f'%{search_value}%'
        rs = nx.xp_nx.FDXQuery(
            sql,
            search_value,
            like,
            like,
            like,
            like,
            sort_field,
            sort_direction,
            sort_field,
            sort_direction,
            sort_field,
            sort_direction,
            sort_field,
            sort_direction,
            sort_field,
            sort_direction,
            sort_field,
            sort_direction,
            limit,
            offset,
        )
        if not rs.error:
            result.status = True
            items = rs.dataset.recordset
            total = _paged_total(nx, count_sql, search_value) if count_sql else len(items)
            result.data = {
                'items': items,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'returned': len(items),
                    'total': total,
                    'has_next': len(items) == limit,
                },
                'filters': {
                    'search': search_value,
                    'sort_field': sort_field,
                    'sort_direction': sort_direction,
                },
            }
        else:
            result.make_error(0, error_message, rs.message)
    except Exception as e:
        result.make_error(0, error_message, str(e))
    return result


def _request_paging(data: Any) -> tuple[str, str, str, int, int]:
    search = (data.get('search') or '').strip()
    sort_field = (data.get('sort_field') or data.get('sort_by') or 'created_at').strip()
    sort_direction = (data.get('sort_direction') or data.get('sort_dir') or 'desc').strip().lower()
    if sort_direction not in {'asc', 'desc'}:
        sort_direction = 'desc'
    limit = int(data.get('limit', 20) or 20)
    offset = int(data.get('offset', 0) or 0)
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    return search, sort_field, sort_direction, limit, offset


def _get_record(nx: Any, sql: str, record_id: Any, error_message: str) -> tuple[NXResult, dict[str, Any] | None]:
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(sql, record_id)
        if rs.error:
            result.make_error(0, error_message, rs.message)
            return result, None
        if rs.dataset.recordcount == 0:
            result.make_error(0, 'Registro nao localizado')
            return result, None
        result.status = True
        return result, rs.dataset.recordset[0]
    except Exception as e:
        result.make_error(0, error_message, str(e))
        return result, None


def admin_accounts_list(nx: Any, data: Any | None = None) -> NXResult:
    payload = data or {}
    if any(key in payload for key in ('search', 'sort_field', 'sort_direction', 'limit', 'offset')):
        search, sort_field, sort_direction, limit, offset = _request_paging(payload)
        paged_result = _paged_master(
            nx,
            SQL_MASTER_ACCOUNTS_LIST_PAGED,
            SQL_MASTER_ACCOUNTS_COUNT,
            search,
            sort_field,
            sort_direction,
            limit,
            offset,
            'Erro ao consultar contas administrativas',
        )
        if paged_result.status:
            return paged_result
    return _list_master(nx, SQL_MASTER_ACCOUNTS_LIST, 'Erro ao consultar contas administrativas')


def admin_accounts_create(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_ACCOUNT_INSERT,
            data.get('code'),
            data.get('name'),
            data.get('document'),
            data.get('phone'),
            data.get('email'),
            data.get('status', 'active'),
            data.get('plan_id'),
            data.get('database_url'),
            data.get('database_host'),
            data.get('database_port'),
            data.get('database_name'),
            data.get('database_user'),
            data.get('database_password'),
            data.get('database_sslmode'),
            data.get('storage_limit_mb', 0),
            data.get('storage_used_mb', 0),
            data.get('expiration_date'),
            data.get('active', True),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                _master_audit_connection(nx),
                record.get('id'),
                _session_user_id(nx),
                'admin',
                'post',
                'accounts',
                record.get('id'),
                '',
                data,
            )
            result.status = True
            result.message = success_message('Conta', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao cadastrar conta', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('conta', 'create'), str(e))
    return result


def admin_accounts_update(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    record_id = data.get('id')
    loaded, current = _get_record(nx, SQL_MASTER_ACCOUNT_BY_ID, record_id, 'Erro ao consultar conta')
    if loaded.error:
        return loaded

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_ACCOUNT_UPDATE,
            data.get('code', current.get('code')),
            data.get('name', current.get('name')),
            data.get('document', current.get('document')),
            data.get('phone', current.get('phone')),
            data.get('email', current.get('email')),
            data.get('status', current.get('status')),
            data.get('plan_id', current.get('plan_id')),
            data.get('database_url', current.get('database_url')),
            data.get('database_host', current.get('database_host')),
            data.get('database_port', current.get('database_port')),
            data.get('database_name', current.get('database_name')),
            data.get('database_user', current.get('database_user')),
            data.get('database_password', current.get('database_password')),
            data.get('database_sslmode', current.get('database_sslmode')),
            data.get('storage_limit_mb', current.get('storage_limit_mb')),
            data.get('storage_used_mb', current.get('storage_used_mb')),
            data.get('expiration_date', current.get('expiration_date')),
            data.get('active', current.get('active')),
            record_id,
        )
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), record_id, _session_user_id(nx), 'admin', 'put', 'accounts', record_id, '', data)
            result.status = True
            result.message = success_message('Conta', 'update')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao atualizar conta', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('conta', 'update'), str(e))
    return result


def admin_accounts_delete(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    record_id = data.get('id')
    loaded, _ = _get_record(nx, SQL_MASTER_ACCOUNT_BY_ID, record_id, 'Erro ao consultar conta')
    if loaded.error:
        return loaded

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_MASTER_ACCOUNT_DELETE, record_id)
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), record_id, _session_user_id(nx), 'admin', 'delete', 'accounts', record_id, '', {'id': record_id})
            result.status = True
            result.message = success_message('Conta', 'delete')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao excluir conta', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('conta', 'delete'), str(e))
    return result


def admin_plans_list(nx: Any, data: Any | None = None) -> NXResult:
    payload = data or {}
    if any(key in payload for key in ('search', 'sort_field', 'sort_direction', 'limit', 'offset')):
        search, sort_field, sort_direction, limit, offset = _request_paging(payload)
        paged_result = _paged_master(nx, SQL_MASTER_PLANS_LIST_PAGED, SQL_MASTER_PLANS_COUNT, search, sort_field, sort_direction, limit, offset, 'Erro ao consultar planos administrativos')
        if paged_result.status:
            return paged_result
    return _list_master(nx, SQL_MASTER_PLANS_LIST, 'Erro ao consultar planos administrativos')


def admin_plans_create(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_PLAN_INSERT,
            data.get('name'),
            data.get('description'),
            data.get('price', 0),
            data.get('max_companies', 0),
            data.get('max_users', 0),
            data.get('max_works', 0),
            data.get('max_storage_mb', 0),
            data.get('active', True),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                _master_audit_connection(nx),
                None,
                _session_user_id(nx),
                'admin',
                'post',
                'plans',
                record.get('id'),
                '',
                data,
            )
            result.status = True
            result.message = success_message('Plano', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao cadastrar plano', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('plano', 'create'), str(e))
    return result


def admin_plans_update(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result
    record_id = data.get('id')
    loaded, current = _get_record(nx, SQL_MASTER_PLAN_BY_ID, record_id, 'Erro ao consultar plano')
    if loaded.error:
        return loaded
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_PLAN_UPDATE,
            data.get('name', current.get('name')),
            data.get('description', current.get('description')),
            data.get('price', current.get('price')),
            data.get('max_companies', current.get('max_companies')),
            data.get('max_users', current.get('max_users')),
            data.get('max_works', current.get('max_works')),
            data.get('max_storage_mb', current.get('max_storage_mb')),
            data.get('active', current.get('active')),
            record_id,
        )
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), None, _session_user_id(nx), 'admin', 'put', 'plans', record_id, '', data)
            result.status = True
            result.message = success_message('Plano', 'update')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao atualizar plano', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('plano', 'update'), str(e))
    return result


def admin_plans_delete(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result
    record_id = data.get('id')
    loaded, _ = _get_record(nx, SQL_MASTER_PLAN_BY_ID, record_id, 'Erro ao consultar plano')
    if loaded.error:
        return loaded
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_MASTER_PLAN_DELETE, record_id)
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), None, _session_user_id(nx), 'admin', 'delete', 'plans', record_id, '', {'id': record_id})
            result.status = True
            result.message = success_message('Plano', 'delete')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao excluir plano', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('plano', 'delete'), str(e))
    return result


def admin_modules_list(nx: Any, data: Any | None = None) -> NXResult:
    payload = data or {}
    if any(key in payload for key in ('search', 'sort_field', 'sort_direction', 'limit', 'offset')):
        search, sort_field, sort_direction, limit, offset = _request_paging(payload)
        paged_result = _paged_master(nx, SQL_MASTER_MODULES_LIST_PAGED, SQL_MASTER_MODULES_COUNT, search, sort_field, sort_direction, limit, offset, 'Erro ao consultar modulos administrativos')
        if paged_result.status:
            return paged_result
    return _list_master(nx, SQL_MASTER_MODULES_LIST, 'Erro ao consultar modulos administrativos')


def admin_modules_create(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        existing_rs = nx.xp_nx.FDXQuery(SQL_MASTER_MODULE_BY_CODE, data.get('code'))
        if existing_rs.error:
            result.make_error(0, 'Erro ao consultar modulo existente', existing_rs.message)
            return result
        if existing_rs.dataset.recordcount > 0:
            result.status = True
            result.message = success_message('Modulo', 'status')
            result.data = existing_rs.dataset.recordset[0]
            return result

        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_MODULE_INSERT,
            data.get('code'),
            data.get('name'),
            data.get('description'),
            data.get('active', True),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                _master_audit_connection(nx),
                None,
                _session_user_id(nx),
                'admin',
                'post',
                'modules',
                record.get('id'),
                '',
                data,
            )
            result.status = True
            result.message = success_message('Modulo', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao cadastrar modulo', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('modulo', 'create'), str(e))
    return result


def admin_modules_update(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result
    record_id = data.get('id')
    loaded, current = _get_record(nx, SQL_MASTER_MODULE_BY_ID, record_id, 'Erro ao consultar modulo')
    if loaded.error:
        return loaded
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_MODULE_UPDATE,
            data.get('code', current.get('code')),
            data.get('name', current.get('name')),
            data.get('description', current.get('description')),
            data.get('active', current.get('active')),
            record_id,
        )
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), None, _session_user_id(nx), 'admin', 'put', 'modules', record_id, '', data)
            result.status = True
            result.message = success_message('Modulo', 'update')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao atualizar modulo', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('modulo', 'update'), str(e))
    return result


def admin_modules_delete(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result
    record_id = data.get('id')
    loaded, _ = _get_record(nx, SQL_MASTER_MODULE_BY_ID, record_id, 'Erro ao consultar modulo')
    if loaded.error:
        return loaded
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_MASTER_MODULE_DELETE, record_id)
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), None, _session_user_id(nx), 'admin', 'delete', 'modules', record_id, '', {'id': record_id})
            result.status = True
            result.message = success_message('Modulo', 'delete')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao excluir modulo', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('modulo', 'delete'), str(e))
    return result


def admin_account_modules_list(nx: Any, data: Any | None = None) -> NXResult:
    payload = data or {}
    if any(key in payload for key in ('search', 'sort_field', 'sort_direction', 'limit', 'offset')):
        search, sort_field, sort_direction, limit, offset = _request_paging(payload)
        paged_result = _paged_master(nx, SQL_ACCOUNT_MODULES_LIST_PAGED, SQL_ACCOUNT_MODULES_COUNT, search, sort_field, sort_direction, limit, offset, 'Erro ao consultar modulos da conta')
        if paged_result.status:
            return paged_result
    return _list_master(nx, SQL_ACCOUNT_MODULES_LIST, 'Erro ao consultar modulos da conta')


def admin_account_modules_create(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        module_id = data.get('module_id')
        module_code = data.get('module_code')

        if not module_id and module_code:
            module_rs = nx.xp_nx.FDXQuery(SQL_MASTER_MODULE_BY_CODE, module_code)
            if module_rs.error:
                result.make_error(0, 'Erro ao localizar modulo pelo codigo', module_rs.message)
                return result
            if module_rs.dataset.recordcount == 0:
                result.make_error(0, f'Modulo nao localizado para o codigo {module_code}')
                return result
            module_id = module_rs.dataset.recordset[0].get('id')

        if not module_id:
            result.make_error(0, 'module_id ou module_code e obrigatorio')
            return result

        existing_rs = nx.xp_nx.FDXQuery(
            SQL_ACCOUNT_MODULE_BY_ACCOUNT_AND_MODULE,
            data.get('account_id'),
            module_id,
        )
        if existing_rs.error:
            result.make_error(0, 'Erro ao verificar vinculo existente', existing_rs.message)
            return result
        if existing_rs.dataset.recordcount > 0:
            result.status = True
            result.message = success_message('Vinculo de modulo', 'status')
            result.data = existing_rs.dataset.recordset[0]
            return result

        rs = nx.xp_nx.FDXQuery(
            SQL_ACCOUNT_MODULE_INSERT,
            data.get('account_id'),
            module_id,
            data.get('active', True),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                _master_audit_connection(nx),
                data.get('account_id'),
                _session_user_id(nx),
                'admin',
                'post',
                'account_modules',
                record.get('id'),
                '',
                {
                    **data,
                    'module_id': module_id,
                },
            )
            result.status = True
            result.message = success_message('Vinculo de modulo', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao vincular modulo a conta', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('vinculo de modulo', 'create'), str(e))
    return result


def admin_account_modules_update(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    record_id = data.get('id')
    loaded, current = _get_record(nx, SQL_ACCOUNT_MODULE_BY_ID, record_id, 'Erro ao consultar vinculo de modulo')
    if loaded.error:
        return loaded

    module_id = data.get('module_id', current.get('module_id'))
    module_code = data.get('module_code')
    if module_code:
        module_rs = nx.xp_nx.FDXQuery(SQL_MASTER_MODULE_BY_CODE, module_code)
        if module_rs.error:
            result = NXResult()
            result.make_error(0, 'Erro ao localizar modulo pelo codigo', module_rs.message)
            return result
        if module_rs.dataset.recordcount == 0:
            result = NXResult()
            result.make_error(0, f'Modulo nao localizado para o codigo {module_code}')
            return result
        module_id = module_rs.dataset.recordset[0].get('id')

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_ACCOUNT_MODULE_UPDATE,
            data.get('account_id', current.get('account_id')),
            module_id,
            data.get('active', current.get('active')),
            record_id,
        )
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), data.get('account_id', current.get('account_id')), _session_user_id(nx), 'admin', 'put', 'account_modules', record_id, '', data)
            result.status = True
            result.message = success_message('Vinculo de modulo', 'update')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao atualizar vinculo de modulo', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('vinculo de modulo', 'update'), str(e))
    return result


def admin_account_modules_delete(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result
    record_id = data.get('id')
    loaded, current = _get_record(nx, SQL_ACCOUNT_MODULE_BY_ID, record_id, 'Erro ao consultar vinculo de modulo')
    if loaded.error:
        return loaded
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_ACCOUNT_MODULE_DELETE, record_id)
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), current.get('account_id'), _session_user_id(nx), 'admin', 'delete', 'account_modules', record_id, '', {'id': record_id})
            result.status = True
            result.message = success_message('Vinculo de modulo', 'delete')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao excluir vinculo de modulo', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('vinculo de modulo', 'delete'), str(e))
    return result


def admin_master_users_list(nx: Any, data: Any | None = None) -> NXResult:
    payload = data or {}
    if any(key in payload for key in ('search', 'sort_field', 'sort_direction', 'limit', 'offset')):
        search, sort_field, sort_direction, limit, offset = _request_paging(payload)
        paged_result = _paged_master(nx, SQL_MASTER_USERS_LIST_PAGED, SQL_MASTER_USERS_COUNT, search, sort_field, sort_direction, limit, offset, 'Erro ao consultar usuarios master')
        if paged_result.status:
            return paged_result
    return _list_master(nx, SQL_MASTER_USERS_LIST, 'Erro ao consultar usuarios master')


def admin_master_users_create(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_MASTER_USER_INSERT,
            data.get('name'),
            data.get('login'),
            hash_password(data.get('password', '')),
            data.get('email'),
            data.get('phone'),
            data.get('role'),
            data.get('active', True),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            audit_data = {
                'name': data.get('name'),
                'login': data.get('login'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'role': data.get('role'),
                'active': data.get('active', True),
            }
            write_audit_log(
                _master_audit_connection(nx),
                None,
                _session_user_id(nx),
                'admin',
                'post',
                'master_users',
                record.get('id'),
                '',
                audit_data,
            )
            result.status = True
            result.message = success_message('Usuario master', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao cadastrar usuario master', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('usuario master', 'create'), str(e))
    return result


def admin_master_users_update(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result
    record_id = data.get('id')
    loaded, current = _get_record(nx, SQL_MASTER_USER_BY_ID, record_id, 'Erro ao consultar usuario master')
    if loaded.error:
        return loaded
    result = NXResult()
    try:
        password = data.get('password')
        if password:
            rs = nx.xp_nx.FDXQuery(
                SQL_MASTER_USER_UPDATE_WITH_PASSWORD,
                data.get('name', current.get('name')),
                data.get('login', current.get('login')),
                hash_password(password),
                data.get('email', current.get('email')),
                data.get('phone', current.get('phone')),
                data.get('role', current.get('role')),
                data.get('active', current.get('active')),
                record_id,
            )
        else:
            rs = nx.xp_nx.FDXQuery(
                SQL_MASTER_USER_UPDATE,
                data.get('name', current.get('name')),
                data.get('login', current.get('login')),
                data.get('email', current.get('email')),
                data.get('phone', current.get('phone')),
                data.get('role', current.get('role')),
                data.get('active', current.get('active')),
                record_id,
            )
        if not rs.error:
            audit_data = {k: v for k, v in data.items() if k != 'password'}
            write_audit_log(_master_audit_connection(nx), None, _session_user_id(nx), 'admin', 'put', 'master_users', record_id, '', audit_data)
            result.status = True
            result.message = success_message('Usuario master', 'update')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao atualizar usuario master', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('usuario master', 'update'), str(e))
    return result


def admin_master_users_delete(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result
    record_id = data.get('id')
    loaded, _ = _get_record(nx, SQL_MASTER_USER_BY_ID, record_id, 'Erro ao consultar usuario master')
    if loaded.error:
        return loaded
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_MASTER_USER_DELETE, record_id)
        if not rs.error:
            write_audit_log(_master_audit_connection(nx), None, _session_user_id(nx), 'admin', 'delete', 'master_users', record_id, '', {'id': record_id})
            result.status = True
            result.message = success_message('Usuario master', 'delete')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'id': record_id}
        else:
            result.make_error(0, 'Erro ao excluir usuario master', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('usuario master', 'delete'), str(e))
    return result


def admin_bootstrap_status(nx: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        rs_meta = nx.xp_nx.FDXQuery(SQL_DATABASE_METADATA_BY_KEY, 'schema_version')
        rs_seed = nx.xp_nx.FDXQuery(SQL_DATABASE_METADATA_BY_KEY, 'master_seed')

        if rs_meta.error:
            result.make_error(0, 'Erro ao consultar metadata de schema', rs_meta.message)
            return result
        if rs_seed.error:
            result.make_error(0, 'Erro ao consultar metadata de seed', rs_seed.message)
            return result

        result.status = True
        result.message = success_message('Status de bootstrap', 'status')
        result.data = {
            'schema_version': rs_meta.dataset.recordset[0] if rs_meta.dataset.recordset else None,
            'master_seed': rs_seed.dataset.recordset[0] if rs_seed.dataset.recordset else None,
        }
    except Exception as e:
        result.make_error(0, process_error_message('status de bootstrap', 'status'), str(e))
    return result


def admin_bootstrap_master(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    return _bootstrap_master_core(nx, data)


def _bootstrap_master_core(nx: Any, data: Any) -> NXResult:
    result = NXResult()
    created = {
        'plans': [],
        'modules': [],
        'master_users': [],
        'metadata': [],
    }
    try:
        schema_version = data.get('schema_version', '1.0.0')
        plan_name = data.get('plan_name', 'Plano Base')
        admin_name = data.get('admin_name', 'Master Admin')
        admin_login = data.get('admin_login', 'admin')
        admin_password = data.get('admin_password', '123456')
        admin_email = data.get('admin_email', 'master@obrax.com')

        default_modules = data.get('modules') or [
            {'code': 'DIARY', 'name': 'Diario de Obra', 'description': 'Modulo de diario'},
            {'code': 'PRODUCTION', 'name': 'Producao', 'description': 'Modulo de producao'},
            {'code': 'AUDIT', 'name': 'Auditoria', 'description': 'Modulo de auditoria'},
        ]

        rs = nx.xp_nx.FDXQuery(SQL_MASTER_PLAN_BY_NAME, plan_name)
        if rs.error:
            result.make_error(0, 'Erro ao verificar plano base', rs.message)
            return result
        if rs.dataset.recordcount == 0:
            inserted = nx.xp_nx.FDXQuery(
                SQL_MASTER_PLAN_INSERT,
                plan_name,
                data.get('plan_description', 'Plano inicial da plataforma'),
                data.get('plan_price', 0),
                data.get('max_companies', 1),
                data.get('max_users', 25),
                data.get('max_works', 10),
                data.get('max_storage_mb', 2048),
                True,
            )
            if inserted.error:
                result.make_error(0, 'Erro ao criar plano base', inserted.message)
                return result
            created['plans'].append(inserted.dataset.recordset[0] if inserted.dataset.recordset else {})

        for module in default_modules:
            rs = nx.xp_nx.FDXQuery(SQL_MASTER_MODULE_BY_CODE, module.get('code'))
            if rs.error:
                result.make_error(0, f"Erro ao verificar modulo {module.get('code')}", rs.message)
                return result
            if rs.dataset.recordcount == 0:
                inserted = nx.xp_nx.FDXQuery(
                    SQL_MASTER_MODULE_INSERT,
                    module.get('code'),
                    module.get('name'),
                    module.get('description'),
                    True,
                )
                if inserted.error:
                    result.make_error(0, f"Erro ao criar modulo {module.get('code')}", inserted.message)
                    return result
                created['modules'].append(inserted.dataset.recordset[0] if inserted.dataset.recordset else {})

        rs = nx.xp_nx.FDXQuery(SQL_MASTER_USER_BY_LOGIN, admin_login)
        if rs.error:
            result.make_error(0, 'Erro ao verificar usuario master inicial', rs.message)
            return result
        if rs.dataset.recordcount == 0:
            inserted = nx.xp_nx.FDXQuery(
                SQL_MASTER_USER_INSERT,
                admin_name,
                admin_login,
                hash_password(admin_password),
                admin_email,
                data.get('admin_phone'),
                data.get('admin_role', 'admin'),
                True,
            )
            if inserted.error:
                result.make_error(0, 'Erro ao criar usuario master inicial', inserted.message)
                return result
            created['master_users'].append(inserted.dataset.recordset[0] if inserted.dataset.recordset else {})

        meta_rows = [
            ('schema_version', schema_version),
            ('master_seed', 'done'),
        ]
        for key, value in meta_rows:
            updated = nx.xp_nx.FDXQuery(SQL_DATABASE_METADATA_UPSERT, key, value)
            if updated.error:
                result.make_error(0, f'Erro ao atualizar metadata {key}', updated.message)
                return result
            created['metadata'].append(updated.dataset.recordset[0] if updated.dataset.recordset else {})

        write_audit_log(
            _master_audit_connection(nx),
            None,
            _session_user_id(nx),
            'admin',
            'bootstrap',
            'master_seed',
            None,
            '',
            {
                'schema_version': schema_version,
                'plan_name': plan_name,
                'admin_login': admin_login,
                'modules': [module.get('code') for module in default_modules],
            },
        )
        result.status = True
        result.message = success_message('Bootstrap master', 'bootstrap')
        result.data = created
    except Exception as e:
        result.make_error(0, process_error_message('bootstrap master', 'bootstrap'), str(e))
    return result


def admin_schema_compatibility(nx: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    required_tables = [
        'database_metadata',
        'plans',
        'modules',
        'accounts',
        'account_modules',
        'master_users',
        'audit_logs',
        'companies',
        'users',
        'projects',
        'daily_logs',
        'production_entries',
    ]

    try:
        table_status = []
        missing_tables = []
        for table_name in required_tables:
            rs = nx.xp_nx.FDXQuery(SQL_TABLE_EXISTS, table_name)
            if rs.error:
                result.make_error(0, f'Erro ao verificar tabela {table_name}', rs.message)
                return result
            exists_flag = bool(rs.dataset.fieldbyname('exists_flag', False))
            table_status.append({'table': table_name, 'exists': exists_flag})
            if not exists_flag:
                missing_tables.append(table_name)

        rs_meta = nx.xp_nx.FDXQuery(SQL_DATABASE_METADATA_BY_KEY, 'schema_version')
        if rs_meta.error:
            result.make_error(0, 'Erro ao consultar schema_version', rs_meta.message)
            return result

        rs_seed = nx.xp_nx.FDXQuery(SQL_DATABASE_METADATA_BY_KEY, 'master_seed')
        if rs_seed.error:
            result.make_error(0, 'Erro ao consultar master_seed', rs_seed.message)
            return result

        schema_version = rs_meta.dataset.recordset[0] if rs_meta.dataset.recordset else None
        master_seed = rs_seed.dataset.recordset[0] if rs_seed.dataset.recordset else None
        compatible = len(missing_tables) == 0

        result.status = True
        result.message = success_message('Compatibilidade de schema', 'compatibility')
        result.data = {
            'compatible': compatible,
            'missing_tables': missing_tables,
            'tables': table_status,
            'schema_version': schema_version,
            'master_seed': master_seed,
        }
    except Exception as e:
        result.make_error(0, process_error_message('compatibilidade de schema', 'compatibility'), str(e))
    return result


def _migration_directory() -> Path:
    return Path(__file__).resolve().parents[2] / 'database' / 'migrations'


def _available_migrations() -> list[dict[str, str]]:
    migrations_dir = _migration_directory()
    if not migrations_dir.exists():
        return []

    migrations = []
    for path in sorted(migrations_dir.glob('*.sql')):
        migrations.append(
            {
                'key': f'migration:{path.name}',
                'file': path.name,
                'version': path.stem.split('_', 1)[0],
                'path': str(path),
            }
        )
    return migrations


def _metadata_value_by_key(nx: Any, metadata_key: str) -> str | None:
    rs = nx.xp_nx.FDXQuery(SQL_DATABASE_METADATA_BY_KEY, metadata_key)
    if rs.error:
        try:
            nx.conn_nx.rollback()
        except Exception:
            pass
        return None
    if rs.dataset.recordcount == 0:
        return None
    return rs.dataset.recordset[0].get('metadata_value')


def admin_migrations_status(nx: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        migrations = []
        for migration in _available_migrations():
            applied_value = _metadata_value_by_key(nx, migration['key'])
            migrations.append(
                {
                    'file': migration['file'],
                    'version': migration['version'],
                    'applied': applied_value is not None,
                    'applied_at': applied_value,
                }
            )

        result.status = True
        result.message = success_message('Migrations', 'status')
        result.data = {
            'migrations': migrations,
            'pending': [item for item in migrations if item['applied'] is False],
            'schema_version': _metadata_value_by_key(nx, 'schema_version'),
        }
    except Exception as e:
        result.make_error(0, process_error_message('status das migrations', 'status'), str(e))
    return result


def admin_migrations_apply(nx: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    return _migrations_apply_core(nx)


def _migrations_apply_core(nx: Any) -> NXResult:
    result = NXResult()
    applied_files = []
    try:
        migrations = _available_migrations()
        if len(migrations) == 0:
            result.status = True
            result.message = success_message('Migrations', 'status')
            result.data = {'applied': [], 'pending': [], 'schema_version': _metadata_value_by_key(nx, 'schema_version')}
            return result

        cursor = nx.conn_nx.cursor()
        for migration in migrations:
            if _metadata_value_by_key(nx, migration['key']):
                continue

            sql_text = Path(migration['path']).read_text(encoding='utf-8')
            cursor.execute(sql_text)
            nx.conn_nx.commit()

            applied_at = migration['file']
            updated = nx.xp_nx.FDXQuery(SQL_DATABASE_METADATA_UPSERT, migration['key'], applied_at)
            if updated.error:
                result.make_error(0, f"Erro ao registrar migration {migration['file']}", updated.message)
                return result

            version_updated = nx.xp_nx.FDXQuery(SQL_DATABASE_METADATA_UPSERT, 'schema_version', migration['version'])
            if version_updated.error:
                result.make_error(0, 'Erro ao atualizar schema_version', version_updated.message)
                return result

            applied_files.append(migration['file'])

        write_audit_log(
            _master_audit_connection(nx),
            None,
            _session_user_id(nx),
            'admin',
            'migrations_apply',
            'database_metadata',
            None,
            '',
            {'applied_files': applied_files},
        )

        result.status = True
        result.message = success_message('Migrations', 'bootstrap')
        result.data = {
            'applied': applied_files,
            'pending': [
                migration['file']
                for migration in migrations
                if migration['file'] not in applied_files and _metadata_value_by_key(nx, migration['key']) is None
            ],
            'schema_version': _metadata_value_by_key(nx, 'schema_version'),
        }
    except Exception as e:
        try:
            nx.conn_nx.rollback()
        except Exception:
            pass
        result.make_error(0, process_error_message('aplicacao de migrations', 'bootstrap'), str(e))
    return result


def public_setup_status(nx: Any) -> NXResult:
    result = NXResult()
    try:
        schema_version = _metadata_value_by_key(nx, 'schema_version')
        master_seed = _metadata_value_by_key(nx, 'master_seed')
        users_result, users_count = _master_users_count(nx)
        if users_result.error:
            return users_result
        result.status = True
        result.message = 'Status de setup inicial carregado com sucesso'
        result.data = {
            'setup_enabled': users_count == 0,
            'master_users_count': users_count,
            'schema_version': schema_version,
            'master_seed': master_seed,
            'schema_ready': schema_version is not None,
        }
    except Exception as e:
        result.make_error(0, 'Erro ao consultar status de setup inicial', str(e))
    return result


def public_setup_initialize(nx: Any, data: Any) -> NXResult:
    migrations_result = _migrations_apply_core(nx)
    if migrations_result.error:
        return migrations_result

    users_result, users_count = _master_users_count(nx)
    if users_result.error:
        return users_result
    if users_count > 0:
        result = NXResult()
        result.make_error(403, 'Setup inicial ja foi executado')
        return result

    bootstrap_result = _bootstrap_master_core(nx, data)
    if bootstrap_result.error:
        return bootstrap_result

    result = NXResult()
    result.status = True
    result.message = 'Setup inicial executado com sucesso'
    result.data = {
        'migrations': migrations_result.data,
        'bootstrap': bootstrap_result.data,
    }
    return result

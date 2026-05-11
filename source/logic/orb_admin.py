from pathlib import Path
from typing import Any

from source.core.system.database import NXMasterConnection
from source.core.system.security import hash_password, write_audit_log
from source.core.system.utils import NXResult, process_error_message, success_message
from source.data.sql.sql_obrax import (
    SQL_ACCOUNT_MODULE_INSERT,
    SQL_ACCOUNT_MODULES_LIST,
    SQL_DATABASE_METADATA_BY_KEY,
    SQL_DATABASE_METADATA_UPSERT,
    SQL_MASTER_ACCOUNT_INSERT,
    SQL_MASTER_ACCOUNTS_LIST,
    SQL_MASTER_MODULE_INSERT,
    SQL_MASTER_MODULE_BY_CODE,
    SQL_MASTER_MODULES_LIST,
    SQL_MASTER_PLAN_INSERT,
    SQL_MASTER_PLAN_BY_NAME,
    SQL_TABLE_EXISTS,
    SQL_MASTER_USER_BY_LOGIN,
    SQL_MASTER_PLANS_LIST,
    SQL_MASTER_USER_INSERT,
    SQL_MASTER_USERS_LIST,
)


def _master_scope_ok(nx: Any) -> NXResult:
    result = NXResult()
    if nx.session.scope != 'master':
        result.make_error(0, 'Token sem permissao master')
        return result
    result.status = True
    return result


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


def admin_accounts_list(nx: Any) -> NXResult:
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
                nx._master,
                record.get('id'),
                nx.session.userid,
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


def admin_plans_list(nx: Any) -> NXResult:
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
                nx._master,
                None,
                nx.session.userid,
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


def admin_modules_list(nx: Any) -> NXResult:
    return _list_master(nx, SQL_MASTER_MODULES_LIST, 'Erro ao consultar modulos administrativos')


def admin_modules_create(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
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
                nx._master,
                None,
                nx.session.userid,
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


def admin_account_modules_list(nx: Any) -> NXResult:
    return _list_master(nx, SQL_ACCOUNT_MODULES_LIST, 'Erro ao consultar modulos da conta')


def admin_account_modules_create(nx: Any, data: Any) -> NXResult:
    result = _master_scope_ok(nx)
    if result.error:
        return result

    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_ACCOUNT_MODULE_INSERT,
            data.get('account_id'),
            data.get('module_id'),
            data.get('active', True),
        )
        if not rs.error:
            record = rs.dataset.recordset[0] if rs.dataset.recordset else {}
            write_audit_log(
                nx._master,
                data.get('account_id'),
                nx.session.userid,
                'admin',
                'post',
                'account_modules',
                record.get('id'),
                '',
                data,
            )
            result.status = True
            result.message = success_message('Vinculo de modulo', 'create')
            result.data = record
        else:
            result.make_error(0, 'Erro ao vincular modulo a conta', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('vinculo de modulo', 'create'), str(e))
    return result


def admin_master_users_list(nx: Any) -> NXResult:
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
                nx._master,
                None,
                nx.session.userid,
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
            nx._master,
            None,
            nx.session.userid,
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
    if rs.error or rs.dataset.recordcount == 0:
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
            nx._master,
            None,
            nx.session.userid,
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

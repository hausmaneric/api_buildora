from source.core.config.config import appConfig
from source.core.system.security import hash_password, write_audit_log
from source.core.system.utils import NXResult, process_error_message, success_message
from source.data.sql.sql_obrax import (
    SQL_TENANT_COMPANIES_LIST,
    SQL_TENANT_COMPANY_BY_DOCUMENT,
    SQL_TENANT_COMPANY_INSERT,
    SQL_TENANT_PERMISSION_BY_CODE,
    SQL_TENANT_PERMISSION_INSERT,
    SQL_TENANT_PERMISSIONS_LIST,
    SQL_TENANT_ROLE_BY_NAME,
    SQL_TENANT_ROLE_INSERT,
    SQL_TENANT_ROLE_PERMISSION_EXISTS,
    SQL_TENANT_ROLE_PERMISSION_INSERT,
    SQL_TENANT_ROLE_PERMISSIONS_LIST,
    SQL_TENANT_ROLES_LIST,
    SQL_TENANT_USER_BY_EMAIL,
    SQL_TENANT_USER_INSERT,
    SQL_TENANT_USERS_LIST,
)
from source.data.models.m_catalog import DEFAULT_FILTER_CATALOG, DEFAULT_MODULE_CATALOG, DEFAULT_STATUS_CATALOG, DEFAULT_TENANT_ROLES


DEFAULT_TENANT_PERMISSIONS = [
    ('dashboard.read', 'Dashboard - leitura'),
    ('companies.read', 'Empresas - leitura'),
    ('companies.write', 'Empresas - escrita'),
    ('users.read', 'Usuarios - leitura'),
    ('users.write', 'Usuarios - escrita'),
    ('roles.read', 'Perfis - leitura'),
    ('roles.write', 'Perfis - escrita'),
    ('permissions.read', 'Permissoes - leitura'),
    ('permissions.write', 'Permissoes - escrita'),
    ('roles.permissions.read', 'Perfis x permissoes - leitura'),
    ('roles.permissions.write', 'Perfis x permissoes - escrita'),
    ('projects.read', 'Obras - leitura'),
    ('projects.write', 'Obras - escrita'),
    ('teams.read', 'Equipes - leitura'),
    ('teams.write', 'Equipes - escrita'),
    ('diary.read', 'Diario - leitura'),
    ('diary.write', 'Diario - escrita'),
    ('diary.approve', 'Diario - aprovacao'),
    ('production.read', 'Producao - leitura'),
    ('production.write', 'Producao - escrita'),
    ('reports.read', 'Relatorios - leitura'),
    ('audit.read', 'Auditoria - leitura'),
]


def tenant_metadata_get(nx):
    result = NXResult()
    try:
        rs_permissions = nx.xp_nx.FDXQuery(SQL_TENANT_PERMISSIONS_LIST)
        rs_roles = nx.xp_nx.FDXQuery(SQL_TENANT_ROLES_LIST)
        if rs_permissions.error:
            result.make_error(0, 'Erro ao consultar metadados de permissao', rs_permissions.message)
        elif rs_roles.error:
            result.make_error(0, 'Erro ao consultar metadados de perfil', rs_roles.message)
        else:
            result.status = True
            result.data = {
                'api': {
                    'name': appConfig.apiName,
                    'version': appConfig.apiVersion,
                },
                'modules': DEFAULT_MODULE_CATALOG,
                'default_roles': [
                    {'name': role_name, 'permissions': permission_codes}
                    for role_name, permission_codes in DEFAULT_TENANT_ROLES.items()
                ],
                'permissions': rs_permissions.dataset.recordset,
                'roles': rs_roles.dataset.recordset,
                'status_catalog': DEFAULT_STATUS_CATALOG,
                'filters': DEFAULT_FILTER_CATALOG,
            }
    except Exception as e:
        result.make_error(0, process_error_message('metadados do ambiente', 'status'), str(e))
    return result


def tenant_companies_list(nx):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TENANT_COMPANIES_LIST)
        if not rs.error:
            result.status = True
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao listar empresas', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta das empresas', str(e))
    return result


def tenant_companies_create(nx, data):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TENANT_COMPANY_INSERT,
            data.get('code'),
            data.get('document'),
            data.get('corporate_name'),
            data.get('fantasy_name'),
            data.get('state_registration'),
            data.get('municipal_registration'),
            data.get('phone'),
            data.get('email'),
            data.get('zipcode'),
            data.get('address'),
            data.get('number'),
            data.get('district'),
            data.get('city'),
            data.get('state'),
            data.get('logo'),
            data.get('active', True),
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Empresa', 'create')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
        else:
            result.make_error(0, 'Erro ao cadastrar empresa do ambiente', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('empresa', 'create'), str(e))
    return result


def tenant_roles_list(nx):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TENANT_ROLES_LIST)
        if not rs.error:
            result.status = True
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao listar perfis', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta dos perfis', str(e))
    return result


def tenant_roles_create(nx, data):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TENANT_ROLE_INSERT,
            data.get('name'),
            data.get('description'),
            data.get('active', True),
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Perfil', 'create')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
        else:
            result.make_error(0, 'Erro ao cadastrar perfil', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('perfil', 'create'), str(e))
    return result


def tenant_permissions_list(nx):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TENANT_PERMISSIONS_LIST)
        if not rs.error:
            result.status = True
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao listar permissoes', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta das permissoes', str(e))
    return result


def tenant_permissions_create(nx, data):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TENANT_PERMISSION_INSERT,
            data.get('code'),
            data.get('name'),
            data.get('description'),
            data.get('active', True),
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Permissao', 'create')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
        else:
            result.make_error(0, 'Erro ao cadastrar permissao', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('permissao', 'create'), str(e))
    return result


def tenant_role_permissions_list(nx):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TENANT_ROLE_PERMISSIONS_LIST)
        if not rs.error:
            result.status = True
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao listar vinculos de permissao', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta dos vinculos de permissao', str(e))
    return result


def tenant_role_permissions_create(nx, data):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TENANT_ROLE_PERMISSION_INSERT,
            data.get('role_id'),
            data.get('permission_id'),
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Vinculo de permissao', 'create')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
        else:
            result.make_error(0, 'Erro ao vincular permissao ao perfil', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('vinculo de permissao', 'create'), str(e))
    return result


def tenant_users_list(nx):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(SQL_TENANT_USERS_LIST)
        if not rs.error:
            result.status = True
            result.data = rs.dataset.recordset
        else:
            result.make_error(0, 'Erro ao listar usuarios do ambiente', rs.message)
    except Exception as e:
        result.make_error(0, 'Falha no processo de consulta dos usuarios', str(e))
    return result


def tenant_users_create(nx, data):
    result = NXResult()
    try:
        rs = nx.xp_nx.FDXQuery(
            SQL_TENANT_USER_INSERT,
            data.get('company_id'),
            data.get('name'),
            data.get('email'),
            hash_password(data.get('password', '')),
            data.get('role_id'),
            data.get('active', True),
        )
        if not rs.error:
            result.status = True
            result.message = success_message('Usuario do ambiente', 'create')
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
        else:
            result.make_error(0, 'Erro ao cadastrar usuario do ambiente', rs.message)
    except Exception as e:
        result.make_error(0, process_error_message('usuario do ambiente', 'create'), str(e))
    return result


def tenant_bootstrap_create(nx, data):
    result = NXResult()
    try:
        company_rs = nx.xp_nx.FDXQuery(SQL_TENANT_COMPANY_BY_DOCUMENT, data.get('company_document'))
        if company_rs.error:
            result.make_error(0, 'Erro ao consultar empresa inicial', company_rs.message)
            return result

        if company_rs.dataset.recordcount > 0:
            company_id = company_rs.dataset.recordset[0]['id']
        else:
            created_company = nx.xp_nx.FDXQuery(
                SQL_TENANT_COMPANY_INSERT,
                data.get('company_code'),
                data.get('company_document'),
                data.get('corporate_name'),
                data.get('fantasy_name'),
                '',
                '',
                data.get('phone'),
                data.get('email'),
                data.get('zipcode'),
                data.get('address'),
                data.get('number'),
                data.get('district'),
                data.get('city'),
                data.get('state'),
                '',
                True,
            )
            if created_company.error:
                result.make_error(0, 'Erro ao criar empresa inicial', created_company.message)
                return result
            company_id = created_company.dataset.recordset[0]['id']

        permission_map = {}
        for code, label in DEFAULT_TENANT_PERMISSIONS:
            permission_rs = nx.xp_nx.FDXQuery(SQL_TENANT_PERMISSION_BY_CODE, code)
            if permission_rs.error:
                result.make_error(0, 'Erro ao consultar permissoes padrao', permission_rs.message)
                return result
            if permission_rs.dataset.recordcount > 0:
                permission_map[code] = permission_rs.dataset.recordset[0]['id']
            else:
                created_permission = nx.xp_nx.FDXQuery(
                    SQL_TENANT_PERMISSION_INSERT,
                    code,
                    label,
                    f'Permissao padrao: {label}',
                    True,
                )
                if created_permission.error:
                    result.make_error(0, 'Erro ao criar permissao padrao', created_permission.message)
                    return result
                permission_map[code] = created_permission.dataset.recordset[0]['id']

        role_map = {}
        for role_name, codes in DEFAULT_TENANT_ROLES.items():
            role_rs = nx.xp_nx.FDXQuery(SQL_TENANT_ROLE_BY_NAME, role_name)
            if role_rs.error:
                result.make_error(0, 'Erro ao consultar perfis padrao', role_rs.message)
                return result
            if role_rs.dataset.recordcount > 0:
                role_id = role_rs.dataset.recordset[0]['id']
            else:
                created_role = nx.xp_nx.FDXQuery(
                    SQL_TENANT_ROLE_INSERT,
                    role_name,
                    f'Perfil padrao do ambiente: {role_name}',
                    True,
                )
                if created_role.error:
                    result.make_error(0, 'Erro ao criar perfil padrao', created_role.message)
                    return result
                role_id = created_role.dataset.recordset[0]['id']
            role_map[role_name] = role_id

            for code in codes:
                permission_id = permission_map[code]
                rel_rs = nx.xp_nx.FDXQuery(SQL_TENANT_ROLE_PERMISSION_EXISTS, role_id, permission_id)
                if rel_rs.error:
                    result.make_error(0, 'Erro ao consultar vinculo de permissao', rel_rs.message)
                    return result
                if rel_rs.dataset.recordcount == 0:
                    created_rel = nx.xp_nx.FDXQuery(SQL_TENANT_ROLE_PERMISSION_INSERT, role_id, permission_id)
                    if created_rel.error:
                        result.make_error(0, 'Erro ao criar vinculo de permissao', created_rel.message)
                        return result

        admin_rs = nx.xp_nx.FDXQuery(SQL_TENANT_USER_BY_EMAIL, data.get('admin_email'))
        if admin_rs.error:
            result.make_error(0, 'Erro ao consultar usuario administrador inicial', admin_rs.message)
            return result

        admin_user = admin_rs.dataset.recordset[0] if admin_rs.dataset.recordcount > 0 else None
        if not admin_user:
            created_admin = nx.xp_nx.FDXQuery(
                SQL_TENANT_USER_INSERT,
                company_id,
                data.get('admin_name'),
                data.get('admin_email'),
                hash_password(data.get('admin_password', '')),
                role_map['Administrador'],
                True,
            )
            if created_admin.error:
                result.make_error(0, 'Erro ao criar administrador inicial', created_admin.message)
                return result
            admin_user = {'id': created_admin.dataset.recordset[0]['id']}

        write_audit_log(
            nx._tenant,
            None,
            nx.session.userid,
            'tenant',
            'bootstrap',
            'companies',
            company_id,
            '',
            {
                'company_id': company_id,
                'admin_user_id': admin_user['id'],
                'roles': list(role_map.keys()),
                'permissions_count': len(permission_map),
            },
        )

        result.status = True
        result.message = success_message('Bootstrap do ambiente', 'bootstrap')
        result.data = {
            'company_id': company_id,
            'admin_user_id': admin_user['id'],
            'roles': role_map,
            'permissions_count': len(permission_map),
        }
    except Exception as e:
        result.make_error(0, process_error_message('bootstrap do ambiente', 'bootstrap'), str(e))
    return result

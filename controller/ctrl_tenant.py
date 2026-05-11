from flask import request
from app import app
from classes.auth_utils import open_tenant_connection, require_tenant_permission
from classes.next_base import NXResult
from classes.obrax_utils import hash_password, write_audit_log
from controller import nxc
from classes.sql.obx_sql import (
    SQL_TENANT_COMPANY_BY_DOCUMENT,
    SQL_TENANT_COMPANIES_LIST,
    SQL_TENANT_COMPANY_INSERT,
    SQL_TENANT_PERMISSION_BY_CODE,
    SQL_TENANT_PERMISSION_INSERT,
    SQL_TENANT_PERMISSIONS_LIST,
    SQL_TENANT_ROLE_BY_NAME,
    SQL_TENANT_ROLE_PERMISSION_EXISTS,
    SQL_TENANT_ROLE_INSERT,
    SQL_TENANT_ROLE_PERMISSION_INSERT,
    SQL_TENANT_ROLE_PERMISSIONS_LIST,
    SQL_TENANT_ROLES_LIST,
    SQL_TENANT_USER_BY_EMAIL,
    SQL_TENANT_USER_INSERT,
    SQL_TENANT_USERS_LIST,
)
from models.tenant import (
    TenantBootstrapInput,
    TenantCompanyInput,
    TenantPermissionInput,
    TenantRoleInput,
    TenantRolePermissionInput,
    TenantUserInput,
)


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
]

DEFAULT_TENANT_ROLES = {
    'Administrador': [code for code, _label in DEFAULT_TENANT_PERMISSIONS],
    'Engenheiro': [
        'dashboard.read',
        'projects.read',
        'projects.write',
        'teams.read',
        'teams.write',
        'diary.read',
        'diary.write',
        'diary.approve',
        'production.read',
        'production.write',
        'reports.read',
    ],
    'Encarregado': [
        'dashboard.read',
        'projects.read',
        'teams.read',
        'diary.read',
        'diary.write',
        'production.read',
        'production.write',
    ],
}

DEFAULT_STATUS_CATALOG = {
    'project_status': [
        {'value': 'active', 'label': 'Ativa'},
        {'value': 'paused', 'label': 'Pausada'},
        {'value': 'finished', 'label': 'Finalizada'},
        {'value': 'cancelled', 'label': 'Cancelada'},
    ],
    'daily_log_status': [
        {'value': 'draft', 'label': 'Rascunho'},
        {'value': 'approved', 'label': 'Aprovado'},
        {'value': 'rejected', 'label': 'Reprovado'},
    ],
    'occurrence_severity': [
        {'value': 'low', 'label': 'Baixa'},
        {'value': 'medium', 'label': 'Media'},
        {'value': 'high', 'label': 'Alta'},
        {'value': 'critical', 'label': 'Critica'},
    ],
    'equipment_status': [
        {'value': 'available', 'label': 'Disponivel'},
        {'value': 'in_use', 'label': 'Em uso'},
        {'value': 'maintenance', 'label': 'Em manutencao'},
        {'value': 'stopped', 'label': 'Parado'},
    ],
    'material_movement_type': [
        {'value': 'entry', 'label': 'Entrada'},
        {'value': 'usage', 'label': 'Consumo'},
        {'value': 'return', 'label': 'Devolucao'},
        {'value': 'loss', 'label': 'Perda'},
    ],
    'signature_type': [
        {'value': 'engineer', 'label': 'Engenheiro'},
        {'value': 'manager', 'label': 'Gestor'},
        {'value': 'client', 'label': 'Cliente'},
        {'value': 'inspector', 'label': 'Fiscal'},
    ],
}

DEFAULT_FILTER_CATALOG = {
    'diary': ['project_id', 'status', 'created_by', 'start_date', 'end_date'],
    'production': ['project_id', 'created_by', 'start_date', 'end_date'],
    'audit_logs': ['module', 'action', 'table_name', 'record_id', 'start_date', 'end_date', 'limit', 'offset'],
    'audit_summary': ['module', 'start_date', 'end_date'],
    'audit_timeline_project': ['project_id', 'limit'],
    'audit_timeline_diary': ['diary_id', 'limit'],
    'reports_project_diaries': ['project_id', 'start_date', 'end_date'],
    'reports_project_summary': ['project_id', 'start_date', 'end_date'],
    'dashboard_user_summary': ['project_id', 'start_date', 'end_date'],
}

DEFAULT_MODULE_CATALOG = [
    {'code': 'dashboard', 'label': 'Dashboard'},
    {'code': 'tenant', 'label': 'Administracao do ambiente'},
    {'code': 'projects', 'label': 'Obras'},
    {'code': 'teams', 'label': 'Equipes'},
    {'code': 'diary', 'label': 'Diario de obra'},
    {'code': 'production', 'label': 'Producao'},
    {'code': 'reports', 'label': 'Relatorios'},
    {'code': 'audit', 'label': 'Auditoria'},
]


def _tenant_connection(permission_code: str | None = None) -> tuple[NXResult, object | None]:
    payload = None
    if permission_code:
        auth, payload = require_tenant_permission(permission_code)
        if auth.error:
            return auth, None

    account_code = request.headers.get('X-Account-Code', '').strip()
    result, tenant, _account = open_tenant_connection(account_code)
    if result.error:
        return result, None
    result.data = {
        'auth_payload': payload,
        'account_code': account_code,
    }
    return result, tenant


@app.route('/api/v1/tenant/metadata', methods=['GET'])
def tenant_metadata():
    opened, tenant = _tenant_connection('permissions.read')
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        rs_permissions = tenant.xp_nx.FDXQuery(SQL_TENANT_PERMISSIONS_LIST)
        rs_roles = tenant.xp_nx.FDXQuery(SQL_TENANT_ROLES_LIST)

        if rs_permissions.error:
            result.make_error(0, 'Erro ao consultar metadados de permissao', rs_permissions.message)
        elif rs_roles.error:
            result.make_error(0, 'Erro ao consultar metadados de perfil', rs_roles.message)
        else:
            result.status = True
            result.data = {
                'api': {
                    'name': nxc.OBRAX_API_NAME,
                    'version': nxc.OBRAX_API_VERSION,
                },
                'modules': DEFAULT_MODULE_CATALOG,
                'default_roles': [
                    {
                        'name': role_name,
                        'permissions': permission_codes,
                    }
                    for role_name, permission_codes in DEFAULT_TENANT_ROLES.items()
                ],
                'permissions': rs_permissions.dataset.recordset,
                'roles': rs_roles.dataset.recordset,
                'status_catalog': DEFAULT_STATUS_CATALOG,
                'filters': DEFAULT_FILTER_CATALOG,
            }
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/tenant/companies', methods=['GET', 'POST'])
def tenant_companies():
    permission = 'companies.read' if request.method == 'GET' else 'companies.write'
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        if request.method == 'GET':
            rs = tenant.xp_nx.FDXQuery(SQL_TENANT_COMPANIES_LIST)
            if rs.error:
                result.make_error(0, 'Erro ao listar empresas', rs.message)
            else:
                result.status = True
                result.data = rs.dataset.recordset
        else:
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
            else:
                payload = TenantCompanyInput.from_dict(data)
                rs = tenant.xp_nx.FDXQuery(
                    SQL_TENANT_COMPANY_INSERT,
                    payload.code,
                    payload.document,
                    payload.corporate_name,
                    payload.fantasy_name,
                    payload.state_registration,
                    payload.municipal_registration,
                    payload.phone,
                    payload.email,
                    payload.zipcode,
                    payload.address,
                    payload.number,
                    payload.district,
                    payload.city,
                    payload.state,
                    payload.logo,
                    payload.active,
                )
                if rs.error:
                    result.make_error(0, 'Erro ao cadastrar empresa do ambiente', rs.message)
                else:
                    result.status = True
                    result.message = 'Empresa cadastrada com sucesso'
                    result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/tenant/roles', methods=['GET', 'POST'])
def tenant_roles():
    permission = 'roles.read' if request.method == 'GET' else 'roles.write'
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        if request.method == 'GET':
            rs = tenant.xp_nx.FDXQuery(SQL_TENANT_ROLES_LIST)
            if rs.error:
                result.make_error(0, 'Erro ao listar perfis', rs.message)
            else:
                result.status = True
                result.data = rs.dataset.recordset
        else:
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
            else:
                payload = TenantRoleInput.from_dict(data)
                rs = tenant.xp_nx.FDXQuery(
                    SQL_TENANT_ROLE_INSERT,
                    payload.name,
                    payload.description,
                    payload.active,
                )
                if rs.error:
                    result.make_error(0, 'Erro ao cadastrar perfil', rs.message)
                else:
                    result.status = True
                    result.message = 'Perfil cadastrado com sucesso'
                    result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/tenant/permissions', methods=['GET', 'POST'])
def tenant_permissions():
    permission = 'permissions.read' if request.method == 'GET' else 'permissions.write'
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        if request.method == 'GET':
            rs = tenant.xp_nx.FDXQuery(SQL_TENANT_PERMISSIONS_LIST)
            if rs.error:
                result.make_error(0, 'Erro ao listar permissões', rs.message)
            else:
                result.status = True
                result.data = rs.dataset.recordset
        else:
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
            else:
                payload = TenantPermissionInput.from_dict(data)
                rs = tenant.xp_nx.FDXQuery(
                    SQL_TENANT_PERMISSION_INSERT,
                    payload.code,
                    payload.name,
                    payload.description,
                    payload.active,
                )
                if rs.error:
                    result.make_error(0, 'Erro ao cadastrar permissão', rs.message)
                else:
                    result.status = True
                    result.message = 'Permissão cadastrada com sucesso'
                    result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/tenant/role_permissions', methods=['GET', 'POST'])
def tenant_role_permissions():
    permission = 'roles.permissions.read' if request.method == 'GET' else 'roles.permissions.write'
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        if request.method == 'GET':
            rs = tenant.xp_nx.FDXQuery(SQL_TENANT_ROLE_PERMISSIONS_LIST)
            if rs.error:
                result.make_error(0, 'Erro ao listar vínculos de permissão', rs.message)
            else:
                result.status = True
                result.data = rs.dataset.recordset
        else:
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
            else:
                payload = TenantRolePermissionInput.from_dict(data)
                rs = tenant.xp_nx.FDXQuery(
                    SQL_TENANT_ROLE_PERMISSION_INSERT,
                    payload.role_id,
                    payload.permission_id,
                )
                if rs.error:
                    result.make_error(0, 'Erro ao vincular permissão ao perfil', rs.message)
                else:
                    result.status = True
                    result.message = 'Vínculo de permissão cadastrado com sucesso'
                    result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/tenant/users', methods=['GET', 'POST'])
def tenant_users():
    permission = 'users.read' if request.method == 'GET' else 'users.write'
    opened, tenant = _tenant_connection(permission)
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        if request.method == 'GET':
            rs = tenant.xp_nx.FDXQuery(SQL_TENANT_USERS_LIST)
            if rs.error:
                result.make_error(0, 'Erro ao listar usuários do ambiente', rs.message)
            else:
                result.status = True
                result.data = rs.dataset.recordset
        else:
            data = request.get_json(silent=True)
            if not data:
                result.make_error(0, 'Dados inválidos enviados')
            else:
                payload = TenantUserInput.from_dict(data)
                rs = tenant.xp_nx.FDXQuery(
                    SQL_TENANT_USER_INSERT,
                    payload.company_id,
                    payload.name,
                    payload.email,
                    hash_password(payload.password),
                    payload.role_id,
                    payload.active,
                )
                if rs.error:
                    result.make_error(0, 'Erro ao cadastrar usuário do ambiente', rs.message)
                else:
                    result.status = True
                    result.message = 'Usuário do ambiente cadastrado com sucesso'
                    result.data = rs.dataset.recordset[0] if rs.dataset.recordset else None
    finally:
        tenant.stop()

    return result.toJSON()


@app.route('/api/v1/tenant/bootstrap', methods=['POST'])
def tenant_bootstrap():
    opened, tenant = _tenant_connection()
    if opened.error:
        return opened.toJSON()

    result = NXResult()
    try:
        data = request.get_json(silent=True)
        if not data:
            result.make_error(0, 'Dados inválidos enviados')
            return result.toJSON()

        payload = TenantBootstrapInput.from_dict(data)

        company_rs = tenant.xp_nx.FDXQuery(SQL_TENANT_COMPANY_BY_DOCUMENT, payload.company_document)
        if company_rs.error:
            result.make_error(0, 'Erro ao consultar empresa inicial', company_rs.message)
            return result.toJSON()

        if company_rs.dataset.recordcount > 0:
            company = company_rs.dataset.recordset[0]
            company_id = company['id']
        else:
            created_company = tenant.xp_nx.FDXQuery(
                SQL_TENANT_COMPANY_INSERT,
                payload.company_code,
                payload.company_document,
                payload.corporate_name,
                payload.fantasy_name,
                '',
                '',
                payload.phone,
                payload.email,
                payload.zipcode,
                payload.address,
                payload.number,
                payload.district,
                payload.city,
                payload.state,
                '',
                True,
            )
            if created_company.error:
                result.make_error(0, 'Erro ao criar empresa inicial', created_company.message)
                return result.toJSON()
            company_id = created_company.dataset.recordset[0]['id']

        permission_map = {}
        for code, label in DEFAULT_TENANT_PERMISSIONS:
            permission_rs = tenant.xp_nx.FDXQuery(SQL_TENANT_PERMISSION_BY_CODE, code)
            if permission_rs.error:
                result.make_error(0, 'Erro ao consultar permissões padrão', permission_rs.message)
                return result.toJSON()
            if permission_rs.dataset.recordcount > 0:
                permission_map[code] = permission_rs.dataset.recordset[0]['id']
            else:
                created_permission = tenant.xp_nx.FDXQuery(
                    SQL_TENANT_PERMISSION_INSERT,
                    code,
                    label,
                    f'Permissão padrão: {label}',
                    True,
                )
                if created_permission.error:
                    result.make_error(0, 'Erro ao criar permissão padrão', created_permission.message)
                    return result.toJSON()
                permission_map[code] = created_permission.dataset.recordset[0]['id']

        role_map = {}
        for role_name, codes in DEFAULT_TENANT_ROLES.items():
            role_rs = tenant.xp_nx.FDXQuery(SQL_TENANT_ROLE_BY_NAME, role_name)
            if role_rs.error:
                result.make_error(0, 'Erro ao consultar perfis padrão', role_rs.message)
                return result.toJSON()
            if role_rs.dataset.recordcount > 0:
                role_id = role_rs.dataset.recordset[0]['id']
            else:
                created_role = tenant.xp_nx.FDXQuery(
                    SQL_TENANT_ROLE_INSERT,
                    role_name,
                    f'Perfil padrão do ambiente: {role_name}',
                    True,
                )
                if created_role.error:
                    result.make_error(0, 'Erro ao criar perfil padrão', created_role.message)
                    return result.toJSON()
                role_id = created_role.dataset.recordset[0]['id']
            role_map[role_name] = role_id

            for code in codes:
                permission_id = permission_map[code]
                rel_rs = tenant.xp_nx.FDXQuery(SQL_TENANT_ROLE_PERMISSION_EXISTS, role_id, permission_id)
                if rel_rs.error:
                    result.make_error(0, 'Erro ao consultar vínculo de permissão', rel_rs.message)
                    return result.toJSON()
                if rel_rs.dataset.recordcount == 0:
                    created_rel = tenant.xp_nx.FDXQuery(SQL_TENANT_ROLE_PERMISSION_INSERT, role_id, permission_id)
                    if created_rel.error:
                        result.make_error(0, 'Erro ao criar vínculo de permissão', created_rel.message)
                        return result.toJSON()

        admin_rs = tenant.xp_nx.FDXQuery(SQL_TENANT_USER_BY_EMAIL, payload.admin_email)
        if admin_rs.error:
            result.make_error(0, 'Erro ao consultar usuário administrador inicial', admin_rs.message)
            return result.toJSON()

        admin_user = admin_rs.dataset.recordset[0] if admin_rs.dataset.recordcount > 0 else None
        if not admin_user:
            created_admin = tenant.xp_nx.FDXQuery(
                SQL_TENANT_USER_INSERT,
                company_id,
                payload.admin_name,
                payload.admin_email,
                hash_password(payload.admin_password),
                role_map['Administrador'],
                True,
            )
            if created_admin.error:
                result.make_error(0, 'Erro ao criar administrador inicial', created_admin.message)
                return result.toJSON()
            admin_user = {'id': created_admin.dataset.recordset[0]['id']}

        auth_payload = opened.data or {}
        write_audit_log(
            tenant,
            None,
            auth_payload.get('auth_payload', {}).get('user_id'),
            'tenant',
            'bootstrap',
            'companies',
            company_id,
            request.remote_addr,
            {
                'company_id': company_id,
                'admin_user_id': admin_user['id'],
                'roles': list(role_map.keys()),
                'permissions_count': len(permission_map),
            },
        )

        result.status = True
        result.message = 'Bootstrap do ambiente executado com sucesso'
        result.data = {
            'company_id': company_id,
            'admin_user_id': admin_user['id'],
            'roles': role_map,
            'permissions_count': len(permission_map),
        }
    finally:
        tenant.stop()

    return result.toJSON()

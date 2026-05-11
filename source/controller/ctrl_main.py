from source.app import app
from source.core.config.config import appConfig
from source.core.system.database import build_connection_string, master_database_ping, validate_master_database_config
from source.core.system.core import NXConnection, NXLoginType
from source.core.system.utils import NXResult, decode_token
from source.logic.orb_diary import _load_diary as load_diary_record
from source.logic.orb_operational import _load_project as load_project_record
from source.logic.orb_operational import _load_aux_daily_log_id as load_aux_daily_log_id
from source.logic.orb_operational import _load_record as load_generic_record
from source.logic.orb_operational import _load_team as load_team_record
from source.logic.orb_production import _load_production as load_production_record
from source.data.sql.sql_obrax import (
    SQL_DAILY_ACTIVITY_BY_ID,
    SQL_DAILY_EQUIPMENT_BY_ID,
    SQL_DAILY_FILE_BY_ID,
    SQL_DAILY_LABOR_BY_ID,
    SQL_DAILY_MATERIAL_BY_ID,
    SQL_DAILY_OCCURRENCE_BY_ID,
    SQL_DAILY_SIGNATURE_BY_ID,
    SQL_TEAM_MEMBER_BY_ID,
)


def _api_examples() -> dict:
    return {
        'create_admin_account': {
            'method': 'POST',
            'path': '/api/v1/admin/accounts/<token_id>',
            'body': {
                'code': 'demo',
                'name': 'Conta Demo',
                'document': '12345678000199',
                'phone': '11999999999',
                'email': 'contato@demo.com',
                'status': 'active',
                'plan_id': 1,
                'database_url': '',
                'database_host': 'localhost',
                'database_port': 5432,
                'database_name': 'obrax_demo',
                'database_user': 'postgres',
                'database_password': 'postgres',
                'database_sslmode': 'require',
                'storage_limit_mb': 1024,
                'storage_used_mb': 0,
                'expiration_date': '2026-12-31',
                'active': True,
            },
        },
        'create_admin_plan': {
            'method': 'POST',
            'path': '/api/v1/admin/plans/<token_id>',
            'body': {
                'name': 'Plano Base',
                'description': 'Plano inicial',
                'price': 199.9,
                'max_companies': 1,
                'max_users': 25,
                'max_works': 10,
                'max_storage_mb': 2048,
                'active': True,
            },
        },
        'create_admin_module': {
            'method': 'POST',
            'path': '/api/v1/admin/modules/<token_id>',
            'body': {
                'code': 'DIARY',
                'name': 'Diario de Obra',
                'description': 'Modulo de diario',
                'active': True,
            },
        },
        'create_admin_account_module': {
            'method': 'POST',
            'path': '/api/v1/admin/account_modules/<token_id>',
            'body': {
                'account_id': 1,
                'module_id': 1,
                'active': True,
            },
        },
        'create_admin_master_user': {
            'method': 'POST',
            'path': '/api/v1/admin/master_users/<token_id>',
            'body': {
                'name': 'Master Admin',
                'login': 'master.admin',
                'password': '123456',
                'email': 'master@obrax.com',
                'phone': '11999999999',
                'role': 'administrator',
                'active': True,
            },
        },
        'master_login': {
            'method': 'POST',
            'path': '/api/v1/auth/master/login/',
            'body': {
                'login': 'admin',
                'password': '123456',
            },
        },
        'tenant_login': {
            'method': 'POST',
            'path': '/api/v1/auth/tenant/login/',
            'headers': {
                'X-Account-Code': 'demo',
            },
            'body': {
                'email': 'admin@empresa.com',
                'password': '123456',
            },
        },
        'tenant_bootstrap': {
            'method': 'POST',
            'path': '/api/v1/tenant/bootstrap/<token_id>',
            'body': {
                'company_code': 'EMP001',
                'company_document': '12345678000199',
                'corporate_name': 'Empresa Demo',
                'fantasy_name': 'Demo',
                'phone': '11999999999',
                'email': 'contato@demo.com',
                'zipcode': '01001000',
                'address': 'Rua Exemplo',
                'number': '100',
                'district': 'Centro',
                'city': 'Sao Paulo',
                'state': 'SP',
                'admin_name': 'Administrador',
                'admin_email': 'admin@demo.com',
                'admin_password': '123456',
            },
        },
        'create_tenant_company': {
            'method': 'POST',
            'path': '/api/v1/tenant/companies/<token_id>',
            'body': {
                'code': 'EMP001',
                'document': '12345678000199',
                'corporate_name': 'Empresa Demo',
                'fantasy_name': 'Demo',
                'phone': '11999999999',
                'email': 'contato@demo.com',
                'city': 'Sao Paulo',
                'state': 'SP',
                'active': True,
            },
        },
        'create_tenant_role': {
            'method': 'POST',
            'path': '/api/v1/tenant/roles/<token_id>',
            'body': {
                'name': 'Engenheiro',
                'description': 'Perfil tecnico',
                'active': True,
            },
        },
        'create_tenant_permission': {
            'method': 'POST',
            'path': '/api/v1/tenant/permissions/<token_id>',
            'body': {
                'code': 'diary.write',
                'name': 'Registrar diario',
                'description': 'Permite criar e editar diarios',
                'module_name': 'diary',
                'active': True,
            },
        },
        'create_tenant_role_permission': {
            'method': 'POST',
            'path': '/api/v1/tenant/role_permissions/<token_id>',
            'body': {
                'role_id': 1,
                'permission_id': 1,
            },
        },
        'create_tenant_user': {
            'method': 'POST',
            'path': '/api/v1/tenant/users/<token_id>',
            'body': {
                'company_id': 1,
                'role_id': 1,
                'name': 'Usuario Obra',
                'email': 'usuario@demo.com',
                'password': '123456',
                'phone': '11999999999',
                'active': True,
            },
        },
        'project_setup': {
            'method': 'POST',
            'path': '/api/v1/projects/setup/<token_id>',
            'body': {
                'project_name': 'Obra Demo',
                'project_code': 'OBR001',
                'client_name': 'Cliente Demo',
                'company_id': 1,
                'engineer_user_id': 1,
                'address': 'Rua da Obra',
                'number': '200',
                'district': 'Centro',
                'city': 'Sao Paulo',
                'state': 'SP',
                'zipcode': '01001000',
                'budget_amount': 100000,
                'status': 'active',
                'main_team_name': 'Equipe Principal',
                'main_team_description': 'Equipe inicial',
                'members': [
                    {
                        'user_id': 1,
                        'member_name': 'Administrador',
                        'role_name': 'Responsavel',
                        'active': True,
                    }
                ],
            },
        },
        'create_diary': {
            'method': 'POST',
            'path': '/api/v1/diary/<token_id>',
            'body': {
                'project_id': 1,
                'work_date': '2026-05-08',
                'weather': 'sunny',
                'summary': 'Atividades do dia',
                'occurrences': 'Sem ocorrencias',
                'status': 'draft',
            },
        },
        'update_diary': {
            'method': 'PUT',
            'path': '/api/v1/diary/<token_id>',
            'body': {
                'id': 1,
                'weather': 'cloudy',
                'summary': 'Atividades revisadas do dia',
                'status': 'pending',
            },
        },
        'create_production': {
            'method': 'POST',
            'path': '/api/v1/production/<token_id>',
            'body': {
                'project_id': 1,
                'reference_date': '2026-05-08',
                'service_name': 'Concretagem',
                'unit': 'm3',
                'planned_quantity': 10,
                'executed_quantity': 8,
                'notes': 'Execucao parcial',
            },
        },
        'create_project': {
            'method': 'POST',
            'path': '/api/v1/projects/<token_id>',
            'body': {
                'company_id': 1,
                'project_code': 'OBR002',
                'project_name': 'Obra Nova',
                'client_name': 'Cliente Novo',
                'engineer_user_id': 1,
                'status': 'active',
            },
        },
        'create_team': {
            'method': 'POST',
            'path': '/api/v1/teams/<token_id>',
            'body': {
                'project_id': 1,
                'team_name': 'Equipe Civil',
                'description': 'Equipe de campo',
                'active': True,
            },
        },
        'create_team_member': {
            'method': 'POST',
            'path': '/api/v1/team_members/<token_id>',
            'body': {
                'team_id': 1,
                'user_id': 1,
                'member_name': 'Joao da Silva',
                'role_name': 'Pedreiro',
                'active': True,
            },
        },
        'create_daily_occurrence': {
            'method': 'POST',
            'path': '/api/v1/daily/occurrences/<token_id>',
            'body': {
                'daily_log_id': 1,
                'description': 'Interrupcao por chuva',
                'occurrence_type': 'weather',
                'resolved': False,
            },
        },
        'create_daily_activity': {
            'method': 'POST',
            'path': '/api/v1/daily/activities/<token_id>',
            'body': {
                'daily_log_id': 1,
                'description': 'Assentamento de blocos',
                'sector_name': 'Alvenaria',
                'quantity_executed': 120,
                'unit': 'm2',
            },
        },
        'create_daily_labor': {
            'method': 'POST',
            'path': '/api/v1/daily/labor/<token_id>',
            'body': {
                'daily_log_id': 1,
                'team_id': 1,
                'role_name': 'Servente',
                'worker_count': 4,
                'worked_hours': 8,
            },
        },
        'create_daily_material': {
            'method': 'POST',
            'path': '/api/v1/daily/materials/<token_id>',
            'body': {
                'daily_log_id': 1,
                'material_name': 'Cimento CP-II',
                'unit': 'saco',
                'quantity': 30,
                'notes': 'Uso na concretagem',
            },
        },
        'create_daily_equipment': {
            'method': 'POST',
            'path': '/api/v1/daily/equipments/<token_id>',
            'body': {
                'daily_log_id': 1,
                'equipment_name': 'Betoneira',
                'quantity': 1,
                'worked_hours': 6,
                'notes': 'Equipamento locado',
            },
        },
        'create_daily_file': {
            'method': 'POST',
            'path': '/api/v1/daily/files/<token_id>',
            'body': {
                'daily_log_id': 1,
                'file_name': 'foto-frente-obra.jpg',
                'file_url': 'https://cdn.demo.local/foto-frente-obra.jpg',
                'file_type': 'image',
            },
        },
        'create_daily_signature': {
            'method': 'POST',
            'path': '/api/v1/daily/signatures/<token_id>',
            'body': {
                'daily_log_id': 1,
                'signed_by_user_id': 1,
                'signed_by_name': 'Administrador',
                'signature_type': 'engineer',
            },
        },
    }


def _api_query_reference() -> dict:
    return {
        'admin.accounts.list': {
            'path': '/api/v1/admin/accounts/<token_id>',
            'query_params': [],
        },
        'admin.plans.list': {
            'path': '/api/v1/admin/plans/<token_id>',
            'query_params': [],
        },
        'admin.modules.list': {
            'path': '/api/v1/admin/modules/<token_id>',
            'query_params': [],
        },
        'admin.account_modules.list': {
            'path': '/api/v1/admin/account_modules/<token_id>',
            'query_params': [],
        },
        'admin.master_users.list': {
            'path': '/api/v1/admin/master_users/<token_id>',
            'query_params': [],
        },
        'tenant.metadata': {
            'path': '/api/v1/tenant/metadata/<token_id>',
            'query_params': [],
        },
        'tenant.companies.list': {
            'path': '/api/v1/tenant/companies/<token_id>',
            'query_params': [],
        },
        'tenant.roles.list': {
            'path': '/api/v1/tenant/roles/<token_id>',
            'query_params': [],
        },
        'tenant.permissions.list': {
            'path': '/api/v1/tenant/permissions/<token_id>',
            'query_params': [],
        },
        'tenant.role_permissions.list': {
            'path': '/api/v1/tenant/role_permissions/<token_id>',
            'query_params': [],
        },
        'tenant.users.list': {
            'path': '/api/v1/tenant/users/<token_id>',
            'query_params': [],
        },
        'projects.list': {
            'path': '/api/v1/projects/<token_id>',
            'query_params': [],
        },
        'teams.list': {
            'path': '/api/v1/teams/<token_id>',
            'query_params': [],
        },
        'team_members.list': {
            'path': '/api/v1/team_members/<token_id>',
            'query_params': [],
        },
        'diary.list': {
            'path': '/api/v1/diary/<token_id>',
            'query_params': ['project_id', 'status', 'created_by', 'start_date', 'end_date'],
        },
        'diary.monthly_export': {
            'path': '/api/v1/diary/monthly-export/<token_id>',
            'query_params': ['project_id', 'start_date', 'end_date'],
        },
        'production.list': {
            'path': '/api/v1/production/<token_id>',
            'query_params': ['project_id', 'created_by', 'start_date', 'end_date'],
        },
        'reports.project_diaries': {
            'path': '/api/v1/reports/projects/diaries/<token_id>',
            'query_params': ['project_id', 'start_date', 'end_date'],
        },
        'reports.project_summary': {
            'path': '/api/v1/reports/projects/summary/<token_id>',
            'query_params': ['project_id', 'start_date', 'end_date'],
        },
        'dashboard.operational': {
            'path': '/api/v1/dashboard/operational/<token_id>',
            'query_params': [],
        },
        'dashboard.users.summary': {
            'path': '/api/v1/dashboard/users/summary/<token_id>',
            'query_params': ['project_id', 'start_date', 'end_date'],
        },
        'audit.logs': {
            'path': '/api/v1/audit/logs/<token_id>',
            'query_params': ['module', 'action', 'table_name', 'record_id', 'start_date', 'end_date', 'limit', 'offset'],
        },
        'audit.summary': {
            'path': '/api/v1/audit/summary/<token_id>',
            'query_params': ['start_date', 'end_date'],
        },
        'audit.projects.timeline': {
            'path': '/api/v1/audit/projects/timeline/<token_id>',
            'query_params': ['project_id', 'start_date', 'end_date'],
        },
        'audit.diaries.timeline': {
            'path': '/api/v1/audit/diaries/timeline/<token_id>',
            'query_params': ['record_id', 'start_date', 'end_date'],
        },
        'indicators.diary.by_user': {
            'path': '/api/v1/indicators/diary/by-user/<token_id>',
            'query_params': ['project_id', 'start_date', 'end_date'],
        },
        'indicators.production.by_user': {
            'path': '/api/v1/indicators/production/by-user/<token_id>',
            'query_params': ['project_id', 'start_date', 'end_date'],
        },
        'daily.occurrences.list': {
            'path': '/api/v1/daily/occurrences/<token_id>',
            'query_params': ['daily_log_id'],
        },
        'daily.activities.list': {
            'path': '/api/v1/daily/activities/<token_id>',
            'query_params': ['daily_log_id'],
        },
        'daily.labor.list': {
            'path': '/api/v1/daily/labor/<token_id>',
            'query_params': ['daily_log_id'],
        },
        'daily.materials.list': {
            'path': '/api/v1/daily/materials/<token_id>',
            'query_params': ['daily_log_id'],
        },
        'daily.equipments.list': {
            'path': '/api/v1/daily/equipments/<token_id>',
            'query_params': ['daily_log_id'],
        },
        'daily.files.list': {
            'path': '/api/v1/daily/files/<token_id>',
            'query_params': ['daily_log_id'],
        },
        'daily.signatures.list': {
            'path': '/api/v1/daily/signatures/<token_id>',
            'query_params': ['daily_log_id'],
        },
    }


def _api_response_examples() -> dict:
    return {
        'list_pattern': {
            'status': True,
            'message': 'Consulta realizada com sucesso',
            'data': [
                {
                    'id': 1,
                    'name': 'Registro Demo',
                }
            ],
        },
        'create_pattern': {
            'status': True,
            'message': 'Registro cadastrado com sucesso',
            'data': {
                'id': 1,
            },
        },
        'diary.detail': {
            'status': True,
            'message': 'Diario carregado com sucesso',
            'data': {
                'daily_log': {
                    'id': 1,
                    'project_id': 1,
                    'work_date': '2026-05-08',
                    'status': 'draft',
                },
                'occurrences': [],
                'activities': [],
                'labor': [],
                'materials': [],
                'equipments': [],
                'files': [],
                'signatures': [],
            },
        },
        'dashboard.operational': {
            'status': True,
            'message': 'Dashboard carregado com sucesso',
            'data': {
                'summary': {
                    'active_projects': 1,
                    'pending_diaries': 2,
                    'approved_diaries': 5,
                },
                'last_diaries': [],
                'project_productivity': [],
            },
        },
        'reports.project_summary': {
            'status': True,
            'message': 'Resumo operacional carregado com sucesso',
            'data': {
                'project_id': 1,
                'total_diaries': 10,
                'approved_diaries': 8,
                'pending_diaries': 2,
                'total_occurrences': 3,
                'open_occurrences': 1,
                'total_executed_quantity': 250,
            },
        },
        'audit.logs': {
            'status': True,
            'message': 'Auditoria carregada com sucesso',
            'data': [
                {
                    'id': 1,
                    'module': 'diary',
                    'action': 'post',
                    'table_name': 'daily_logs',
                    'record_id': 1,
                    'user_name': 'Administrador',
                    'created_at': '2026-05-08T10:00:00',
                }
            ],
        },
    }


def _module_catalog() -> dict:
    return {
        'admin': {
            'capabilities': [
                'manage_accounts',
                'manage_plans',
                'manage_modules',
                'manage_master_users',
            ],
            'permissions': ['scope:master'],
            'routes': [
                '/api/v1/admin/accounts/<token_id>',
                '/api/v1/admin/plans/<token_id>',
                '/api/v1/admin/modules/<token_id>',
                '/api/v1/admin/account_modules/<token_id>',
                '/api/v1/admin/master_users/<token_id>',
            ],
            'payload_keys': [
                'admin.accounts.create',
                'admin.plans.create',
                'admin.modules.create',
                'admin.account_modules.create',
                'admin.master_users.create',
            ],
            'query_keys': [
                'admin.accounts.list',
                'admin.plans.list',
                'admin.modules.list',
                'admin.account_modules.list',
                'admin.master_users.list',
            ],
            'response_keys': ['list_pattern', 'create_pattern'],
        },
        'auth': {
            'capabilities': [
                'login_master',
                'login_tenant',
            ],
            'permissions': [],
            'routes': [
                '/api/v1/auth/master/login/',
                '/api/v1/auth/tenant/login/',
            ],
            'payload_keys': ['auth.master_login', 'auth.tenant_login'],
            'query_keys': [],
            'response_keys': ['create_pattern'],
        },
        'tenant': {
            'capabilities': [
                'view_tenant_metadata',
                'manage_companies',
                'manage_roles',
                'manage_permissions',
                'manage_users',
                'bootstrap_tenant',
            ],
            'permissions': [
                'tenant.metadata.read',
                'tenant.company.read',
                'tenant.company.write',
                'tenant.role.read',
                'tenant.role.write',
                'tenant.permission.read',
                'tenant.permission.write',
                'tenant.user.read',
                'tenant.user.write',
            ],
            'routes': [
                '/api/v1/tenant/metadata/<token_id>',
                '/api/v1/tenant/companies/<token_id>',
                '/api/v1/tenant/roles/<token_id>',
                '/api/v1/tenant/permissions/<token_id>',
                '/api/v1/tenant/role_permissions/<token_id>',
                '/api/v1/tenant/users/<token_id>',
                '/api/v1/tenant/bootstrap/<token_id>',
            ],
            'payload_keys': [
                'tenant.companies.create',
                'tenant.roles.create',
                'tenant.permissions.create',
                'tenant.role_permissions.create',
                'tenant.users.create',
                'tenant.bootstrap',
            ],
            'query_keys': [
                'tenant.metadata',
                'tenant.companies.list',
                'tenant.roles.list',
                'tenant.permissions.list',
                'tenant.role_permissions.list',
                'tenant.users.list',
            ],
            'response_keys': ['list_pattern', 'create_pattern'],
        },
        'operational': {
            'capabilities': [
                'view_operational_dashboard',
                'manage_projects',
                'manage_teams',
                'manage_team_members',
                'setup_project',
                'view_operational_reports',
            ],
            'permissions': [
                'project.read',
                'project.write',
                'team.read',
                'team.write',
                'report.project.read',
                'dashboard.operational.read',
            ],
            'routes': [
                '/api/v1/dashboard/operational/<token_id>',
                '/api/v1/projects/<token_id>',
                '/api/v1/projects/setup/<token_id>',
                '/api/v1/teams/<token_id>',
                '/api/v1/team_members/<token_id>',
                '/api/v1/reports/projects/diaries/<token_id>',
                '/api/v1/reports/projects/summary/<token_id>',
            ],
            'payload_keys': [
                'projects.setup',
                'projects.create',
                'projects.update',
                'teams.create',
                'teams.update',
                'team_members.create',
                'team_members.update',
            ],
            'query_keys': [
                'projects.list',
                'teams.list',
                'team_members.list',
                'reports.project_diaries',
                'reports.project_summary',
                'dashboard.operational',
                'dashboard.users.summary',
            ],
            'response_keys': ['list_pattern', 'create_pattern', 'dashboard.operational', 'reports.project_summary'],
        },
        'diary': {
            'capabilities': [
                'view_diary',
                'manage_diary',
                'approve_diary',
                'reject_diary',
                'export_diary',
                'manage_daily_resources',
            ],
            'permissions': [
                'diary.read',
                'diary.write',
                'diary.approve',
                'daily.occurrence.write',
                'daily.activity.write',
                'daily.labor.write',
                'daily.material.write',
                'daily.equipment.write',
                'daily.file.write',
                'daily.signature.write',
            ],
            'routes': [
                '/api/v1/diary/<token_id>',
                '/api/v1/diary/<diary_id>/<token_id>',
                '/api/v1/diary/<diary_id>/export/<token_id>',
                '/api/v1/diary/monthly-export/<token_id>',
                '/api/v1/diary/<diary_id>/approve/<token_id>',
                '/api/v1/diary/<diary_id>/reject/<token_id>',
                '/api/v1/daily/occurrences/<token_id>',
                '/api/v1/daily/activities/<token_id>',
                '/api/v1/daily/labor/<token_id>',
                '/api/v1/daily/materials/<token_id>',
                '/api/v1/daily/equipments/<token_id>',
                '/api/v1/daily/files/<token_id>',
                '/api/v1/daily/signatures/<token_id>',
            ],
            'payload_keys': [
                'diary.create',
                'diary.update',
                'daily.occurrences.create',
                'daily.occurrences.update',
                'daily.activities.create',
                'daily.activities.update',
                'daily.labor.create',
                'daily.labor.update',
                'daily.materials.create',
                'daily.materials.update',
                'daily.equipments.create',
                'daily.equipments.update',
                'daily.files.create',
                'daily.files.update',
                'daily.signatures.create',
                'daily.signatures.update',
            ],
            'query_keys': [
                'diary.list',
                'diary.monthly_export',
                'daily.occurrences.list',
                'daily.activities.list',
                'daily.labor.list',
                'daily.materials.list',
                'daily.equipments.list',
                'daily.files.list',
                'daily.signatures.list',
            ],
            'response_keys': ['list_pattern', 'create_pattern', 'diary.detail'],
        },
        'production': {
            'capabilities': [
                'manage_production',
                'view_audit_logs',
                'view_audit_summary',
                'view_audit_timeline',
                'view_indicators',
            ],
            'permissions': [
                'production.read',
                'production.write',
                'audit.read',
                'indicator.read',
            ],
            'routes': [
                '/api/v1/production/<token_id>',
                '/api/v1/audit/logs/<token_id>',
                '/api/v1/audit/summary/<token_id>',
                '/api/v1/audit/projects/timeline/<token_id>',
                '/api/v1/audit/diaries/timeline/<token_id>',
                '/api/v1/indicators/diary/by-user/<token_id>',
                '/api/v1/indicators/production/by-user/<token_id>',
            ],
            'payload_keys': ['production.create', 'production.update'],
            'query_keys': [
                'production.list',
                'audit.logs',
                'audit.summary',
                'audit.projects.timeline',
                'audit.diaries.timeline',
                'indicators.diary.by_user',
                'indicators.production.by_user',
            ],
            'response_keys': ['list_pattern', 'create_pattern', 'audit.logs'],
        },
    }


def _build_module_catalog() -> dict:
    payloads = {
        'admin.accounts.create': {
            'required_fields': ['code', 'name'],
            'optional_fields': [
                'document', 'phone', 'email', 'status', 'plan_id', 'database_url',
                'database_host', 'database_port', 'database_name', 'database_user',
                'database_password', 'database_sslmode', 'storage_limit_mb',
                'storage_used_mb', 'expiration_date', 'active',
            ],
        },
        'admin.plans.create': {
            'required_fields': ['name'],
            'optional_fields': ['description', 'price', 'max_companies', 'max_users', 'max_works', 'max_storage_mb', 'active'],
        },
        'admin.modules.create': {
            'required_fields': ['code', 'name'],
            'optional_fields': ['description', 'active'],
        },
        'admin.account_modules.create': {
            'required_fields': ['account_id', 'module_id'],
            'optional_fields': ['active'],
        },
        'admin.master_users.create': {
            'required_fields': ['name', 'login', 'password'],
            'optional_fields': ['email', 'phone', 'role', 'active'],
        },
        'auth.master_login': {'required_fields': ['login', 'password'], 'optional_fields': []},
        'auth.tenant_login': {'required_headers': ['X-Account-Code'], 'required_fields': ['email', 'password'], 'optional_fields': []},
        'tenant.companies.create': {
            'required_fields': ['code', 'document', 'corporate_name'],
            'optional_fields': ['fantasy_name', 'phone', 'email', 'zipcode', 'address', 'number', 'district', 'city', 'state', 'active'],
        },
        'tenant.roles.create': {'required_fields': ['name'], 'optional_fields': ['description', 'active']},
        'tenant.permissions.create': {'required_fields': ['code', 'name'], 'optional_fields': ['description', 'module_name', 'active']},
        'tenant.role_permissions.create': {'required_fields': ['role_id', 'permission_id'], 'optional_fields': []},
        'tenant.users.create': {'required_fields': ['company_id', 'name', 'email', 'password'], 'optional_fields': ['role_id', 'phone', 'active']},
        'tenant.bootstrap': {
            'required_fields': ['company_code', 'company_document', 'corporate_name', 'admin_name', 'admin_email', 'admin_password'],
            'optional_fields': ['fantasy_name', 'phone', 'email', 'zipcode', 'address', 'number', 'district', 'city', 'state'],
        },
        'projects.setup': {
            'required_fields': ['project_name', 'project_code', 'company_id', 'main_team_name'],
            'optional_fields': ['client_name', 'engineer_user_id', 'address', 'number', 'district', 'city', 'state', 'zipcode', 'budget_amount', 'status', 'main_team_description', 'members'],
        },
        'projects.create': {
            'required_fields': ['company_id', 'project_code', 'project_name'],
            'optional_fields': ['client_name', 'engineer_user_id', 'address', 'number', 'district', 'city', 'state', 'zipcode', 'budget_amount', 'status'],
        },
        'projects.update': {
            'required_fields': ['id'],
            'optional_fields': ['company_id', 'project_code', 'project_name', 'client_name', 'engineer_user_id', 'address', 'number', 'district', 'city', 'state', 'zipcode', 'budget_amount', 'status'],
        },
        'teams.create': {'required_fields': ['project_id', 'team_name'], 'optional_fields': ['description', 'active']},
        'teams.update': {'required_fields': ['id'], 'optional_fields': ['project_id', 'team_name', 'description', 'active']},
        'team_members.create': {'required_fields': ['team_id', 'member_name'], 'optional_fields': ['user_id', 'role_name', 'active']},
        'team_members.update': {'required_fields': ['id'], 'optional_fields': ['team_id', 'user_id', 'member_name', 'role_name', 'active']},
        'diary.create': {'required_fields': ['project_id', 'work_date'], 'optional_fields': ['weather', 'summary', 'occurrences', 'status', 'created_by']},
        'diary.update': {'required_fields': ['id'], 'optional_fields': ['project_id', 'work_date', 'weather', 'summary', 'occurrences', 'status']},
        'production.create': {'required_fields': ['project_id', 'reference_date', 'service_name'], 'optional_fields': ['unit', 'planned_quantity', 'executed_quantity', 'notes', 'created_by']},
        'production.update': {'required_fields': ['id'], 'optional_fields': ['project_id', 'reference_date', 'service_name', 'unit', 'planned_quantity', 'executed_quantity', 'notes']},
        'daily.occurrences.create': {'required_fields': ['daily_log_id', 'description'], 'optional_fields': ['occurrence_type', 'resolved']},
        'daily.occurrences.update': {'required_fields': ['id'], 'optional_fields': ['description', 'occurrence_type', 'resolved']},
        'daily.activities.create': {'required_fields': ['daily_log_id', 'description'], 'optional_fields': ['sector_name', 'quantity_executed', 'unit']},
        'daily.activities.update': {'required_fields': ['id'], 'optional_fields': ['description', 'sector_name', 'quantity_executed', 'unit']},
        'daily.labor.create': {'required_fields': ['daily_log_id', 'role_name'], 'optional_fields': ['team_id', 'worker_count', 'worked_hours']},
        'daily.labor.update': {'required_fields': ['id'], 'optional_fields': ['team_id', 'role_name', 'worker_count', 'worked_hours']},
        'daily.materials.create': {'required_fields': ['daily_log_id', 'material_name'], 'optional_fields': ['unit', 'quantity', 'notes']},
        'daily.materials.update': {'required_fields': ['id'], 'optional_fields': ['material_name', 'unit', 'quantity', 'notes']},
        'daily.equipments.create': {'required_fields': ['daily_log_id', 'equipment_name'], 'optional_fields': ['quantity', 'worked_hours', 'notes']},
        'daily.equipments.update': {'required_fields': ['id'], 'optional_fields': ['equipment_name', 'quantity', 'worked_hours', 'notes']},
        'daily.files.create': {'required_fields': ['daily_log_id', 'file_name'], 'optional_fields': ['file_url', 'file_type']},
        'daily.files.update': {'required_fields': ['id'], 'optional_fields': ['file_name', 'file_url', 'file_type']},
        'daily.signatures.create': {'required_fields': ['daily_log_id', 'signed_by_name'], 'optional_fields': ['signed_by_user_id', 'signature_type']},
        'daily.signatures.update': {'required_fields': ['id'], 'optional_fields': ['signed_by_user_id', 'signed_by_name', 'signature_type']},
    }

    queries = _api_query_reference()
    responses = _api_response_examples()
    examples = _api_examples()
    catalog = {}

    for module_name, module_info in _module_catalog().items():
        catalog[module_name] = {
            'capabilities': module_info['capabilities'],
            'permissions': module_info['permissions'],
            'routes': module_info['routes'],
            'payloads': {key: payloads[key] for key in module_info['payload_keys'] if key in payloads},
            'queries': {key: queries[key] for key in module_info['query_keys'] if key in queries},
            'responses': {key: responses[key] for key in module_info['response_keys'] if key in responses},
            'examples': {key: value for key, value in examples.items() if any(fragment in key for fragment in module_name.split('_')) or module_name == 'auth' and 'login' in key},
        }

    catalog['tenant']['examples'].update({
        'tenant_bootstrap': examples['tenant_bootstrap'],
        'create_tenant_company': examples['create_tenant_company'],
        'create_tenant_role': examples['create_tenant_role'],
        'create_tenant_permission': examples['create_tenant_permission'],
        'create_tenant_role_permission': examples['create_tenant_role_permission'],
        'create_tenant_user': examples['create_tenant_user'],
    })
    catalog['admin']['examples'].update({
        'create_admin_account': examples['create_admin_account'],
        'create_admin_plan': examples['create_admin_plan'],
        'create_admin_module': examples['create_admin_module'],
        'create_admin_account_module': examples['create_admin_account_module'],
        'create_admin_master_user': examples['create_admin_master_user'],
    })
    catalog['operational']['examples'].update({
        'project_setup': examples['project_setup'],
        'create_project': examples['create_project'],
        'create_team': examples['create_team'],
        'create_team_member': examples['create_team_member'],
    })
    catalog['diary']['examples'].update({
        'create_diary': examples['create_diary'],
        'update_diary': examples['update_diary'],
        'create_daily_occurrence': examples['create_daily_occurrence'],
        'create_daily_activity': examples['create_daily_activity'],
        'create_daily_labor': examples['create_daily_labor'],
        'create_daily_material': examples['create_daily_material'],
        'create_daily_equipment': examples['create_daily_equipment'],
        'create_daily_file': examples['create_daily_file'],
        'create_daily_signature': examples['create_daily_signature'],
    })
    catalog['production']['examples'].update({
        'create_production': examples['create_production'],
    })
    catalog['auth']['examples'].update({
        'master_login': examples['master_login'],
        'tenant_login': examples['tenant_login'],
    })
    return catalog


def _permission_matches(session_permissions: list[str], required_permission: str) -> bool:
    if required_permission in session_permissions:
        return True

    required_base = required_permission.replace('.read', '').replace('.write', '').replace('.approve', '')
    for permission in session_permissions:
        permission_base = permission.replace('.read', '').replace('.write', '').replace('.approve', '')
        if permission_base == required_base:
            return True
    return False


def _resolve_catalog_for_session(scope: str, permissions: list[str]) -> dict:
    catalog = _build_module_catalog()
    resolved = {}

    for module_name, module_data in catalog.items():
        resolved_module = dict(module_data)
        resolved_module['visible'] = False
        resolved_module['granted_permissions'] = []

        if scope == 'master':
            resolved_module['visible'] = module_name in {'admin', 'auth'}
            if resolved_module['visible']:
                resolved_module['granted_permissions'] = module_data.get('permissions', [])
        elif scope == 'tenant':
            module_permissions = module_data.get('permissions', [])
            granted_permissions = [
                permission
                for permission in module_permissions
                if _permission_matches(permissions, permission)
            ]
            if module_name == 'auth':
                resolved_module['visible'] = True
            elif module_name == 'admin':
                resolved_module['visible'] = False
            else:
                resolved_module['visible'] = len(granted_permissions) > 0
            resolved_module['granted_permissions'] = granted_permissions

        resolved[module_name] = resolved_module

    return resolved


def _resolve_login_type_by_token(token_id: str) -> NXLoginType:
    login_type = NXLoginType.ORB
    preview = token_id.replace('Bearer ', '').strip()
    if preview:
        try:
            payload = decode_token(preview)
            if payload.get('scope') == 'tenant':
                return NXLoginType.SYSTEM
        except Exception:
            return NXLoginType.ORB
    return login_type


def _visible_modules(catalog: dict) -> list[str]:
    return [module_name for module_name, module_data in catalog.items() if module_data.get('visible') is True]


def _screen_title(entity: str | None = None) -> str:
    titles = {
        None: 'Painel da Aplicação',
        'diary': 'Diário de Obra',
        'project': 'Obra',
        'production': 'Produção',
        'team': 'Equipe',
        'team_member': 'Membro da Equipe',
        'occurrence': 'Ocorrência do Diário',
        'activity': 'Atividade do Diário',
        'labor': 'Mão de Obra do Diário',
        'material': 'Material do Diário',
        'equipment': 'Equipamento do Diário',
        'file': 'Arquivo do Diário',
        'signature': 'Assinatura do Diário',
    }
    return titles.get(entity, 'Tela da Aplicação')


def _screen_breadcrumbs(entity: str | None = None, record_id: int | None = None) -> list[dict]:
    base = [{'label': 'Início', 'route': '/'}]
    maps = {
        None: [{'label': 'Painel', 'route': '/visao-geral/dashboard'}],
        'diary': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Diário', 'route': '/operacao/diario'}],
        'project': [{'label': 'Cadastros', 'route': '/cadastros'}, {'label': 'Obras', 'route': '/cadastros/obras'}],
        'production': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Produção', 'route': '/operacao/producao'}],
        'team': [{'label': 'Cadastros', 'route': '/cadastros'}, {'label': 'Equipes', 'route': '/cadastros/equipes'}],
        'team_member': [{'label': 'Cadastros', 'route': '/cadastros'}, {'label': 'Membros da Equipe', 'route': '/cadastros/membros-equipe'}],
        'occurrence': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Ocorrências', 'route': '/operacao/diario/ocorrencias'}],
        'activity': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Atividades', 'route': '/operacao/diario/atividades'}],
        'labor': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Mão de Obra', 'route': '/operacao/diario/mao-de-obra'}],
        'material': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Materiais', 'route': '/operacao/diario/materiais'}],
        'equipment': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Equipamentos', 'route': '/operacao/diario/equipamentos'}],
        'file': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Arquivos', 'route': '/operacao/diario/arquivos'}],
        'signature': [{'label': 'Operação', 'route': '/operacao'}, {'label': 'Assinaturas', 'route': '/operacao/diario/assinaturas'}],
    }
    trail = maps.get(entity, [])
    if entity and record_id:
        trail.append({'label': f'Registro #{record_id}', 'route': ''})
    return base + trail


def _screen_empty_state(entity: str | None = None) -> dict:
    states = {
        None: {
            'title': 'Nenhum conteúdo inicial disponível',
            'description': 'Use os módulos visíveis para começar a operação do ambiente.',
            'action_label': 'Abrir dashboard',
            'action_route': '/visao-geral/dashboard',
        },
        'diary': {
            'title': 'Nenhum diário localizado',
            'description': 'Cadastre ou selecione um diário para continuar.',
            'action_label': 'Novo diário',
            'action_route': '/operacao/diario/novo',
        },
        'project': {
            'title': 'Nenhuma obra localizada',
            'description': 'Cadastre uma obra para começar a operação.',
            'action_label': 'Nova obra',
            'action_route': '/cadastros/obras',
        },
        'production': {
            'title': 'Nenhum lançamento de produção localizado',
            'description': 'Crie um lançamento para acompanhar a execução.',
            'action_label': 'Nova produção',
            'action_route': '/operacao/producao',
        },
        'team': {
            'title': 'Nenhuma equipe localizada',
            'description': 'Cadastre uma equipe para vincular pessoas à operação.',
            'action_label': 'Nova equipe',
            'action_route': '/cadastros/equipes',
        },
    }
    return states.get(entity, {
        'title': 'Nenhum registro localizado',
        'description': 'Selecione um registro válido para continuar.',
        'action_label': 'Voltar',
        'action_route': '/',
    })


def _page_action_item(
    key: str,
    visible: bool,
    enabled: bool,
    route: str,
    label: str,
    icon: str,
    reason: str = '',
    priority: int = 50,
    intent: str = 'neutral',
    style: str = 'default',
    confirmation: dict | None = None,
    api_action: bool = False,
    http_method: str = 'GET',
    api_path: str = '',
    required_params: list[str] | None = None,
    payload_schema: dict | None = None,
) -> dict:
    return {
        'key': key,
        'visible': visible,
        'enabled': enabled,
        'disabled_reason': reason if not enabled else '',
        'route': route,
        'label': label,
        'icon': icon,
        'priority': priority,
        'intent': intent,
        'style': style,
        'confirmation': confirmation,
        'api_action': api_action,
        'http_method': http_method,
        'api_path': api_path,
        'required_params': required_params or [],
        'payload_schema': payload_schema or {},
    }


def _screen_base_page_actions(scope: str, permissions: list[str], entity: str | None = None) -> list[dict]:
    capabilities = _resolved_capabilities(scope, permissions)
    is_master = scope == 'master'
    actions = []

    if entity is None:
        actions.extend([
            _page_action_item(
                'open_dashboard',
                capabilities['can_view_operational_dashboard'],
                capabilities['can_view_operational_dashboard'],
                '/visao-geral/dashboard',
                'Abrir dashboard',
                'bar-chart-3',
                'Dashboard nao disponivel para a sessao',
                100,
                'primary',
                'solid',
            ),
            _page_action_item(
                'open_feature_map',
                True,
                True,
                '/api/v1/feature-map',
                'Ver navegacao',
                'layout-dashboard',
                '',
                80,
                'neutral',
                'ghost',
            ),
        ])
        if is_master:
            actions.append(_page_action_item(
                'new_account',
                capabilities['can_manage_accounts'],
                capabilities['can_manage_accounts'],
                '/cadastros/contas',
                'Nova conta',
                'briefcase',
                'Acesso restrito ao escopo master',
                95,
                'primary',
                'solid',
            ))
        return actions

    entity_map = {
        'diary': [
            _page_action_item('new_diary', capabilities['can_create_diary'], capabilities['can_create_diary'], '/operacao/diario/novo', 'Novo diário', 'file-plus', 'Permissão para criar diário não concedida', 100, 'primary', 'solid'),
            _page_action_item('list_diary', capabilities['can_edit_diary'] or capabilities['can_export_diary'], capabilities['can_edit_diary'] or capabilities['can_export_diary'], '/operacao/diario', 'Listar diários', 'file-text', 'Visualização de diários não permitida', 80, 'neutral', 'outline'),
        ],
        'project': [
            _page_action_item('new_project', capabilities['can_manage_projects'], capabilities['can_manage_projects'], '/cadastros/obras', 'Nova obra', 'hard-hat', 'Permissão de obras não concedida', 100, 'primary', 'solid'),
            _page_action_item('project_reports', capabilities['can_view_reports'], capabilities['can_view_reports'], '/visao-geral/relatorios', 'Relatórios', 'file-bar-chart', 'Relatórios não permitidos', 85, 'neutral', 'outline'),
        ],
        'production': [
            _page_action_item('new_production', capabilities['can_manage_production'], capabilities['can_manage_production'], '/operacao/producao', 'Nova produção', 'factory', 'Permissão de produção não concedida', 100, 'primary', 'solid'),
            _page_action_item('production_indicators', capabilities['can_view_indicators'], capabilities['can_view_indicators'], '/visao-geral/indicadores', 'Indicadores', 'gauge', 'Indicadores não permitidos', 80, 'neutral', 'outline'),
        ],
        'team': [
            _page_action_item('new_team', capabilities['can_manage_teams'], capabilities['can_manage_teams'], '/cadastros/equipes', 'Nova equipe', 'users-round', 'Permissão de equipes não concedida', 100, 'primary', 'solid'),
            _page_action_item('list_members', capabilities['can_manage_team_members'], capabilities['can_manage_team_members'], '/cadastros/membros-equipe', 'Membros', 'id-card', 'Permissão de membros não concedida', 82, 'neutral', 'outline'),
        ],
        'team_member': [
            _page_action_item('new_team_member', capabilities['can_manage_team_members'], capabilities['can_manage_team_members'], '/cadastros/membros-equipe', 'Novo membro', 'user-plus', 'Permissão de membros não concedida', 100, 'primary', 'solid'),
            _page_action_item('list_teams', capabilities['can_manage_teams'], capabilities['can_manage_teams'], '/cadastros/equipes', 'Equipes', 'users-round', 'Permissão de equipes não concedida', 75, 'neutral', 'outline'),
        ],
        'occurrence': [
            _page_action_item('new_occurrence', capabilities['can_manage_daily_resources'], capabilities['can_manage_daily_resources'], '/operacao/diario/ocorrencias', 'Nova ocorrência', 'alert-triangle', 'Permissões de recursos do diário não concedidas', 100, 'primary', 'solid'),
        ],
        'activity': [
            _page_action_item('new_activity', capabilities['can_manage_daily_resources'], capabilities['can_manage_daily_resources'], '/operacao/diario/atividades', 'Nova atividade', 'list-todo', 'Permissões de recursos do diário não concedidas', 100, 'primary', 'solid'),
        ],
        'labor': [
            _page_action_item('new_labor', capabilities['can_manage_daily_resources'], capabilities['can_manage_daily_resources'], '/operacao/diario/mao-de-obra', 'Nova mão de obra', 'hammer', 'Permissões de recursos do diário não concedidas', 100, 'primary', 'solid'),
        ],
        'material': [
            _page_action_item('new_material', capabilities['can_manage_daily_resources'], capabilities['can_manage_daily_resources'], '/operacao/diario/materiais', 'Novo material', 'package', 'Permissões de recursos do diário não concedidas', 100, 'primary', 'solid'),
        ],
        'equipment': [
            _page_action_item('new_equipment', capabilities['can_manage_daily_resources'], capabilities['can_manage_daily_resources'], '/operacao/diario/equipamentos', 'Novo equipamento', 'wrench', 'Permissões de recursos do diário não concedidas', 100, 'primary', 'solid'),
        ],
        'file': [
            _page_action_item('new_file', capabilities['can_manage_daily_resources'], capabilities['can_manage_daily_resources'], '/operacao/diario/arquivos', 'Novo arquivo', 'paperclip', 'Permissões de recursos do diário não concedidas', 100, 'primary', 'solid'),
        ],
        'signature': [
            _page_action_item('new_signature', capabilities['can_manage_daily_resources'], capabilities['can_manage_daily_resources'], '/operacao/diario/assinaturas', 'Nova assinatura', 'pen-square', 'Permissões de recursos do diário não concedidas', 100, 'primary', 'solid'),
        ],
    }

    return entity_map.get(entity, [
        _page_action_item('go_back', True, True, '/', 'Voltar', 'arrow-left', '', 60, 'neutral', 'ghost'),
    ])


def _context_to_page_actions(context: dict | None) -> list[dict]:
    if not context:
        return []

    action_map = []
    entity = (context or {}).get('entity', '')
    record_id = (context or {}).get('record_id', '<record_id>')

    for key, action in (context.get('actions') or {}).items():
        intent = 'neutral'
        style = 'outline'
        confirmation = None
        api_action = False
        http_method = 'GET'
        api_path = ''
        required_params = []
        payload_schema = {}

        if key in {'approve'}:
            intent = 'primary'
            style = 'solid'
            api_action = True
            http_method = 'POST'
            if entity == 'diary':
                api_path = f'/api/v1/diary/{record_id}/approve/<token_id>'
                required_params = ['token_id', 'record_id']
            confirmation = {
                'required': True,
                'title': 'Confirmar aprovação',
                'message': 'Deseja realmente aprovar este registro?',
                'confirm_label': 'Aprovar',
            }
        elif key in {'edit', 'export', 'view', 'reports', 'dashboard', 'indicators', 'members'}:
            intent = 'neutral'
            style = 'outline'
            if key == 'export' and entity == 'diary':
                api_path = f'/api/v1/diary/{record_id}/export/<token_id>'
                required_params = ['token_id', 'record_id']
        elif key in {'reject', 'delete'}:
            intent = 'danger'
            style = 'solid' if key == 'delete' else 'outline'
            api_action = True
            http_method = 'DELETE' if key == 'delete' else 'POST'
            if key == 'reject' and entity == 'diary':
                api_path = f'/api/v1/diary/{record_id}/reject/<token_id>'
                required_params = ['token_id', 'record_id']
            elif key == 'delete':
                delete_map = {
                    'production': f'/api/v1/production/<token_id>?id={record_id}',
                    'project': f'/api/v1/projects/<token_id>?id={record_id}',
                    'team': f'/api/v1/teams/<token_id>?id={record_id}',
                    'team_member': f'/api/v1/team_members/<token_id>?id={record_id}',
                    'occurrence': f'/api/v1/daily/occurrences/<token_id>?id={record_id}',
                    'activity': f'/api/v1/daily/activities/<token_id>?id={record_id}',
                    'labor': f'/api/v1/daily/labor/<token_id>?id={record_id}',
                    'material': f'/api/v1/daily/materials/<token_id>?id={record_id}',
                    'equipment': f'/api/v1/daily/equipments/<token_id>?id={record_id}',
                    'file': f'/api/v1/daily/files/<token_id>?id={record_id}',
                    'signature': f'/api/v1/daily/signatures/<token_id>?id={record_id}',
                }
                api_path = delete_map.get(entity, '')
                required_params = ['token_id', 'id']
                payload_schema = {
                    'location': 'query',
                    'fields': {
                        'id': {'type': 'integer', 'required': True},
                    },
                }
            confirmation = {
                'required': True,
                'title': 'Confirmar ação',
                'message': 'Deseja realmente continuar com esta operação?',
                'confirm_label': action.get('label', 'Confirmar'),
            }

        action_map.append(_page_action_item(
            key,
            bool(action.get('visible', False)),
            bool(action.get('enabled', False)),
            action.get('route', ''),
            action.get('label', key.title()),
            action.get('icon', 'circle'),
            action.get('disabled_reason', ''),
            90 if key in {'approve', 'edit', 'export'} else 70,
            intent,
            style,
            confirmation,
            api_action,
            http_method,
            api_path,
            required_params,
            payload_schema,
        ))

    return action_map


def _merge_page_actions(*groups: list[dict]) -> list[dict]:
    merged = {}

    for group in groups:
        for action in group:
            key = action.get('key')
            if not key:
                continue
            current = merged.get(key)
            if current is None or action.get('priority', 0) > current.get('priority', 0):
                merged[key] = action

    return sorted(
        [action for action in merged.values() if action.get('visible', False)],
        key=lambda item: item.get('priority', 0),
        reverse=True,
    )


def _split_page_actions(actions: list[dict]) -> tuple[dict | None, list[dict]]:
    if not actions:
        return None, []
    primary = actions[0]
    secondary = actions[1:]
    return primary, secondary


def _screen_context_payload(nx: NXConnection, entity: str | None = None, record_id: int | None = None) -> dict:
    resolved_catalog = _resolve_catalog_for_session(nx.session.scope, nx.session.permissions)
    capabilities = _resolved_capabilities(nx.session.scope, nx.session.permissions)
    feature_map = _feature_map(nx.session.scope, nx.session.permissions)
    base_page_actions = _screen_base_page_actions(nx.session.scope, nx.session.permissions, entity)
    primary_action, secondary_actions = _split_page_actions(base_page_actions)

    payload = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'scope': nx.session.scope,
        'mode': 'master' if nx.session.scope == 'master' else 'tenant',
        'page_title': _screen_title(entity),
        'breadcrumbs': _screen_breadcrumbs(entity, record_id),
        'empty_state': _screen_empty_state(entity),
        'primary_action': primary_action,
        'secondary_actions': secondary_actions,
        'page_actions': base_page_actions,
        'session': {
            'user_id': nx.session.userid,
            'account_code': nx.session.account_code,
            'permissions': nx.session.permissions,
            'visible_modules': _visible_modules(resolved_catalog),
        },
        'capabilities': capabilities,
        'feature_map': feature_map,
    }

    if entity and record_id:
        if entity == 'diary':
            loaded, record = load_diary_record(nx, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _diary_context_actions(nx.session.scope, nx.session.permissions, record)
        elif entity == 'project':
            loaded, record = load_project_record(nx, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _project_context_actions(nx.session.scope, nx.session.permissions, record)
        elif entity == 'production':
            loaded, record = load_production_record(nx, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _production_context_actions(nx.session.scope, nx.session.permissions, record)
        elif entity == 'team':
            loaded, record = load_team_record(nx, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _team_context_actions(nx.session.scope, nx.session.permissions, record)
        elif entity == 'team_member':
            loaded, record = load_generic_record(nx, SQL_TEAM_MEMBER_BY_ID, record_id, 'Membro da equipe nao localizado', 'Erro ao consultar membro da equipe')
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _team_member_context_actions(nx.session.scope, nx.session.permissions, record)
        elif entity == 'occurrence':
            loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_OCCURRENCE_BY_ID, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'occurrence', record_id, diary_id)
        elif entity == 'activity':
            loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_ACTIVITY_BY_ID, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'activity', record_id, diary_id)
        elif entity == 'labor':
            loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_LABOR_BY_ID, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'labor', record_id, diary_id)
        elif entity == 'material':
            loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_MATERIAL_BY_ID, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'material', record_id, diary_id)
        elif entity == 'equipment':
            loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_EQUIPMENT_BY_ID, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'equipment', record_id, diary_id)
        elif entity == 'file':
            loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_FILE_BY_ID, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'file', record_id, diary_id)
        elif entity == 'signature':
            loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_SIGNATURE_BY_ID, record_id)
            if loaded.error:
                return {'error': loaded.toJSON()}
            payload['context'] = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'signature', record_id, diary_id)
        payload['page_actions'] = _merge_page_actions(
            base_page_actions,
            _context_to_page_actions(payload.get('context')),
        )
        payload['primary_action'], payload['secondary_actions'] = _split_page_actions(payload['page_actions'])

    return payload


def _resolved_capabilities(scope: str, permissions: list[str]) -> dict:
    def has(permission_code: str) -> bool:
        return _permission_matches(permissions, permission_code)

    if scope == 'master':
        return {
            'can_manage_accounts': True,
            'can_manage_plans': True,
            'can_manage_modules': True,
            'can_manage_master_users': True,
            'can_view_tenant_metadata': False,
            'can_manage_companies': False,
            'can_manage_roles': False,
            'can_manage_permissions': False,
            'can_manage_tenant_users': False,
            'can_manage_projects': False,
            'can_manage_teams': False,
            'can_manage_team_members': False,
            'can_view_operational_dashboard': False,
            'can_view_reports': False,
            'can_create_diary': False,
            'can_edit_diary': False,
            'can_approve_diary': False,
            'can_export_diary': False,
            'can_manage_daily_resources': False,
            'can_manage_production': False,
            'can_view_audit': False,
            'can_view_indicators': False,
        }

    return {
        'can_manage_accounts': False,
        'can_manage_plans': False,
        'can_manage_modules': False,
        'can_manage_master_users': False,
        'can_view_tenant_metadata': has('tenant.metadata.read'),
        'can_manage_companies': has('tenant.company.write') or has('companies.write'),
        'can_manage_roles': has('tenant.role.write') or has('roles.write'),
        'can_manage_permissions': has('tenant.permission.write') or has('permissions.write'),
        'can_manage_tenant_users': has('tenant.user.write') or has('users.write'),
        'can_manage_projects': has('project.write') or has('projects.write'),
        'can_manage_teams': has('team.write') or has('teams.write'),
        'can_manage_team_members': has('team.write') or has('teams.write'),
        'can_view_operational_dashboard': has('dashboard.operational.read') or has('dashboard.read'),
        'can_view_reports': has('report.project.read') or has('reports.read'),
        'can_create_diary': has('diary.write'),
        'can_edit_diary': has('diary.write'),
        'can_approve_diary': has('diary.approve'),
        'can_export_diary': has('diary.read'),
        'can_manage_daily_resources': any(
            has(code)
            for code in [
                'daily.occurrence.write',
                'daily.activity.write',
                'daily.labor.write',
                'daily.material.write',
                'daily.equipment.write',
                'daily.file.write',
                'daily.signature.write',
            ]
        ),
        'can_manage_production': has('production.write'),
        'can_view_audit': has('audit.read'),
        'can_view_indicators': has('indicator.read'),
    }


def _context_action_item(visible: bool, enabled: bool, reason: str, route: str, label: str, icon: str) -> dict:
    return {
        'visible': visible,
        'enabled': enabled,
        'disabled_reason': reason if not enabled else '',
        'route': route,
        'label': label,
        'icon': icon,
    }


def _diary_context_actions(scope: str, permissions: list[str], diary: dict | None) -> dict:
    capabilities = _resolved_capabilities(scope, permissions)
    status = (diary or {}).get('status', '')
    is_approved = status == 'approved'

    can_view = capabilities['can_export_diary'] or capabilities['can_edit_diary'] or capabilities['can_approve_diary']
    can_edit = capabilities['can_edit_diary'] and not is_approved
    can_delete = capabilities['can_edit_diary'] and not is_approved
    can_approve = capabilities['can_approve_diary'] and not is_approved
    can_reject = capabilities['can_approve_diary'] and status not in {'approved', 'rejected'}
    can_export = capabilities['can_export_diary']

    return {
        'entity': 'diary',
        'record_id': (diary or {}).get('id'),
        'status': status,
        'actions': {
            'view': _context_action_item(can_view, can_view, 'Visualizacao nao permitida', '/operacao/diario', 'Visualizar', 'eye'),
            'edit': _context_action_item(capabilities['can_edit_diary'], can_edit, 'Diario aprovado nao pode ser alterado' if is_approved else 'Edicao nao permitida', '/operacao/diario/editar', 'Editar', 'pencil'),
            'delete': _context_action_item(capabilities['can_edit_diary'], can_delete, 'Diario aprovado nao pode ser excluido' if is_approved else 'Exclusao nao permitida', '/operacao/diario/excluir', 'Excluir', 'trash-2'),
            'approve': _context_action_item(capabilities['can_approve_diary'], can_approve, 'Diario ja aprovado ou sem permissao' if not can_approve else '', '/operacao/diario/aprovar', 'Aprovar', 'badge-check'),
            'reject': _context_action_item(capabilities['can_approve_diary'], can_reject, 'Diario nao pode ser reprovado neste status', '/operacao/diario/reprovar', 'Reprovar', 'ban'),
            'export': _context_action_item(can_export, can_export, 'Exportacao nao permitida', '/operacao/diario/exportar', 'Exportar', 'file-output'),
        },
    }


def _project_context_actions(scope: str, permissions: list[str], project: dict | None) -> dict:
    capabilities = _resolved_capabilities(scope, permissions)
    status = (project or {}).get('status', '')
    is_closed = status in {'finished', 'cancelled', 'archived'}

    can_view = capabilities['can_manage_projects'] or capabilities['can_view_reports']
    can_edit = capabilities['can_manage_projects'] and not is_closed
    can_delete = capabilities['can_manage_projects'] and not is_closed
    can_report = capabilities['can_view_reports']
    can_dashboard = capabilities['can_view_operational_dashboard']

    return {
        'entity': 'project',
        'record_id': (project or {}).get('id'),
        'status': status,
        'actions': {
            'view': _context_action_item(can_view, can_view, 'Visualizacao nao permitida', '/cadastros/obras', 'Visualizar', 'eye'),
            'edit': _context_action_item(capabilities['can_manage_projects'], can_edit, 'Obra encerrada nao pode ser alterada' if is_closed else 'Edicao nao permitida', '/cadastros/obras/editar', 'Editar', 'pencil'),
            'delete': _context_action_item(capabilities['can_manage_projects'], can_delete, 'Obra encerrada nao pode ser excluida' if is_closed else 'Exclusao nao permitida', '/cadastros/obras/excluir', 'Excluir', 'trash-2'),
            'reports': _context_action_item(can_report, can_report, 'Relatorios nao permitidos', '/visao-geral/relatorios', 'Relatórios', 'file-bar-chart'),
            'dashboard': _context_action_item(can_dashboard, can_dashboard, 'Dashboard nao permitido', '/visao-geral/dashboard', 'Dashboard', 'bar-chart-3'),
        },
    }


def _production_context_actions(scope: str, permissions: list[str], production: dict | None) -> dict:
    capabilities = _resolved_capabilities(scope, permissions)

    can_view = capabilities['can_manage_production'] or capabilities['can_view_indicators']
    can_edit = capabilities['can_manage_production']
    can_delete = capabilities['can_manage_production']
    can_indicators = capabilities['can_view_indicators']

    return {
        'entity': 'production',
        'record_id': (production or {}).get('id'),
        'status': 'active',
        'actions': {
            'view': _context_action_item(can_view, can_view, 'Visualizacao nao permitida', '/operacao/producao', 'Visualizar', 'eye'),
            'edit': _context_action_item(capabilities['can_manage_production'], can_edit, 'Edicao de producao nao permitida', '/operacao/producao/editar', 'Editar', 'pencil'),
            'delete': _context_action_item(capabilities['can_manage_production'], can_delete, 'Exclusao de producao nao permitida', '/operacao/producao/excluir', 'Excluir', 'trash-2'),
            'indicators': _context_action_item(can_indicators, can_indicators, 'Indicadores nao permitidos', '/visao-geral/indicadores', 'Indicadores', 'gauge'),
        },
    }


def _team_context_actions(scope: str, permissions: list[str], team: dict | None) -> dict:
    capabilities = _resolved_capabilities(scope, permissions)
    active = bool((team or {}).get('active', False))

    can_view = capabilities['can_manage_teams'] or capabilities['can_manage_team_members']
    can_edit = capabilities['can_manage_teams'] and active
    can_delete = capabilities['can_manage_teams'] and active
    can_members = capabilities['can_manage_team_members']

    return {
        'entity': 'team',
        'record_id': (team or {}).get('id'),
        'status': 'active' if active else 'inactive',
        'actions': {
            'view': _context_action_item(can_view, can_view, 'Visualizacao nao permitida', '/cadastros/equipes', 'Visualizar', 'eye'),
            'edit': _context_action_item(capabilities['can_manage_teams'], can_edit, 'Equipe inativa nao pode ser alterada' if not active else 'Edicao de equipe nao permitida', '/cadastros/equipes/editar', 'Editar', 'pencil'),
            'delete': _context_action_item(capabilities['can_manage_teams'], can_delete, 'Equipe inativa nao pode ser excluida' if not active else 'Exclusao de equipe nao permitida', '/cadastros/equipes/excluir', 'Excluir', 'trash-2'),
            'members': _context_action_item(can_members, can_members, 'Gerenciamento de membros nao permitido', '/cadastros/membros-equipe', 'Membros', 'users-round'),
        },
    }


def _team_member_context_actions(scope: str, permissions: list[str], team_member: dict | None) -> dict:
    capabilities = _resolved_capabilities(scope, permissions)
    active = bool((team_member or {}).get('active', False))
    can_view = capabilities['can_manage_team_members'] or capabilities['can_manage_teams']
    can_edit = capabilities['can_manage_team_members'] and active
    can_delete = capabilities['can_manage_team_members'] and active

    return {
        'entity': 'team_member',
        'record_id': (team_member or {}).get('id'),
        'status': 'active' if active else 'inactive',
        'actions': {
            'view': _context_action_item(can_view, can_view, 'Visualizacao nao permitida', '/cadastros/membros-equipe', 'Visualizar', 'eye'),
            'edit': _context_action_item(capabilities['can_manage_team_members'], can_edit, 'Membro inativo nao pode ser alterado' if not active else 'Edicao de membro nao permitida', '/cadastros/membros-equipe/editar', 'Editar', 'pencil'),
            'delete': _context_action_item(capabilities['can_manage_team_members'], can_delete, 'Membro inativo nao pode ser excluido' if not active else 'Exclusao de membro nao permitida', '/cadastros/membros-equipe/excluir', 'Excluir', 'trash-2'),
        },
    }


def _daily_resource_context_actions(scope: str, permissions: list[str], entity: str, record_id: int, diary_id: int | None) -> dict:
    capabilities = _resolved_capabilities(scope, permissions)
    can_manage = capabilities['can_manage_daily_resources']
    base_route_map = {
        'occurrence': ('/operacao/diario/ocorrencias', 'Ocorrência', 'alert-triangle'),
        'activity': ('/operacao/diario/atividades', 'Atividade', 'list-todo'),
        'labor': ('/operacao/diario/mao-de-obra', 'Mão de Obra', 'hammer'),
        'material': ('/operacao/diario/materiais', 'Material', 'package'),
        'equipment': ('/operacao/diario/equipamentos', 'Equipamento', 'wrench'),
        'file': ('/operacao/diario/arquivos', 'Arquivo', 'paperclip'),
        'signature': ('/operacao/diario/assinaturas', 'Assinatura', 'pen-square'),
    }
    route, label, icon = base_route_map[entity]
    can_view = can_manage or capabilities['can_export_diary']

    return {
        'entity': entity,
        'record_id': record_id,
        'status': 'linked',
        'daily_log_id': diary_id,
        'actions': {
            'view': _context_action_item(can_view, can_view, 'Visualizacao nao permitida', route, f'Visualizar {label}', 'eye'),
            'edit': _context_action_item(can_manage, can_manage, f'Edicao de {label.lower()} nao permitida', f'{route}/editar', f'Editar {label}', 'pencil'),
            'delete': _context_action_item(can_manage, can_manage, f'Exclusao de {label.lower()} nao permitida', f'{route}/excluir', f'Excluir {label}', 'trash-2'),
        },
    }


def _feature_map(scope: str, permissions: list[str]) -> dict:
    capabilities = _resolved_capabilities(scope, permissions)
    is_master = scope == 'master'

    return {
        'cadastros': {
            'visible': any([
                capabilities['can_manage_accounts'],
                capabilities['can_manage_companies'],
                capabilities['can_manage_roles'],
                capabilities['can_manage_permissions'],
                capabilities['can_manage_tenant_users'],
                capabilities['can_manage_projects'],
                capabilities['can_manage_teams'],
                capabilities['can_manage_team_members'],
            ]),
            'order': 1,
            'priority': 80,
            'label': 'Cadastros',
            'icon': 'folder-open',
            'home_route': '/cadastros',
            'items': {
                'accounts': {
                    'visible': capabilities['can_manage_accounts'],
                    'enabled': capabilities['can_manage_accounts'],
                    'disabled_reason': '' if capabilities['can_manage_accounts'] else 'Acesso restrito ao escopo master',
                    'badge': 'admin' if capabilities['can_manage_accounts'] else '',
                    'order': 1,
                    'priority': 90,
                    'label': 'Contas',
                    'icon': 'briefcase',
                    'route': '/cadastros/contas',
                },
                'companies': {
                    'visible': capabilities['can_manage_companies'],
                    'enabled': capabilities['can_manage_companies'],
                    'disabled_reason': '' if capabilities['can_manage_companies'] else 'Permissão de empresas não concedida',
                    'badge': 'tenant' if capabilities['can_manage_companies'] else '',
                    'order': 2,
                    'priority': 85,
                    'label': 'Empresas',
                    'icon': 'building',
                    'route': '/cadastros/empresas',
                },
                'roles': {
                    'visible': capabilities['can_manage_roles'],
                    'enabled': capabilities['can_manage_roles'],
                    'disabled_reason': '' if capabilities['can_manage_roles'] else 'Permissão de perfis não concedida',
                    'badge': '' ,
                    'order': 3,
                    'priority': 70,
                    'label': 'Perfis',
                    'icon': 'shield',
                    'route': '/cadastros/perfis',
                },
                'permissions': {
                    'visible': capabilities['can_manage_permissions'],
                    'enabled': capabilities['can_manage_permissions'],
                    'disabled_reason': '' if capabilities['can_manage_permissions'] else 'Permissão de permissões não concedida',
                    'badge': '' ,
                    'order': 4,
                    'priority': 65,
                    'label': 'Permissões',
                    'icon': 'key',
                    'route': '/cadastros/permissoes',
                },
                'users': {
                    'visible': capabilities['can_manage_tenant_users'],
                    'enabled': capabilities['can_manage_tenant_users'],
                    'disabled_reason': '' if capabilities['can_manage_tenant_users'] else 'Permissão de usuários não concedida',
                    'badge': '' ,
                    'order': 5,
                    'priority': 88,
                    'label': 'Usuários',
                    'icon': 'users',
                    'route': '/cadastros/usuarios',
                },
                'projects': {
                    'visible': capabilities['can_manage_projects'],
                    'enabled': capabilities['can_manage_projects'],
                    'disabled_reason': '' if capabilities['can_manage_projects'] else 'Permissão de obras não concedida',
                    'badge': 'core' if capabilities['can_manage_projects'] else '',
                    'order': 6,
                    'priority': 95,
                    'label': 'Obras',
                    'icon': 'hard-hat',
                    'route': '/cadastros/obras',
                },
                'teams': {
                    'visible': capabilities['can_manage_teams'],
                    'enabled': capabilities['can_manage_teams'],
                    'disabled_reason': '' if capabilities['can_manage_teams'] else 'Permissão de equipes não concedida',
                    'badge': '' ,
                    'order': 7,
                    'priority': 78,
                    'label': 'Equipes',
                    'icon': 'users-round',
                    'route': '/cadastros/equipes',
                },
                'team_members': {
                    'visible': capabilities['can_manage_team_members'],
                    'enabled': capabilities['can_manage_team_members'],
                    'disabled_reason': '' if capabilities['can_manage_team_members'] else 'Permissão de membros não concedida',
                    'badge': '' ,
                    'order': 8,
                    'priority': 72,
                    'label': 'Membros da Equipe',
                    'icon': 'id-card',
                    'route': '/cadastros/membros-equipe',
                },
            },
        },
        'operacao': {
            'visible': any([
                capabilities['can_create_diary'],
                capabilities['can_edit_diary'],
                capabilities['can_approve_diary'],
                capabilities['can_manage_daily_resources'],
                capabilities['can_manage_production'],
            ]),
            'order': 2,
            'priority': 100,
            'label': 'Operação',
            'icon': 'clipboard-list',
            'home_route': '/operacao',
            'items': {
                'diary_create': {
                    'visible': capabilities['can_create_diary'],
                    'enabled': capabilities['can_create_diary'],
                    'disabled_reason': '' if capabilities['can_create_diary'] else 'Permissão para criar diário não concedida',
                    'badge': 'novo' if capabilities['can_create_diary'] else '',
                    'order': 1,
                    'priority': 100,
                    'label': 'Novo Diário',
                    'icon': 'file-plus',
                    'route': '/operacao/diario/novo',
                },
                'diary_edit': {
                    'visible': capabilities['can_edit_diary'],
                    'enabled': capabilities['can_edit_diary'],
                    'disabled_reason': '' if capabilities['can_edit_diary'] else 'Permissão para editar diário não concedida',
                    'badge': '' ,
                    'order': 2,
                    'priority': 96,
                    'label': 'Diários',
                    'icon': 'file-text',
                    'route': '/operacao/diario',
                },
                'diary_approve': {
                    'visible': capabilities['can_approve_diary'],
                    'enabled': capabilities['can_approve_diary'],
                    'disabled_reason': '' if capabilities['can_approve_diary'] else 'Permissão para aprovar diário não concedida',
                    'badge': 'aprovação' if capabilities['can_approve_diary'] else '',
                    'order': 3,
                    'priority': 92,
                    'label': 'Aprovações',
                    'icon': 'badge-check',
                    'route': '/operacao/diario/aprovacoes',
                },
                'daily_resources': {
                    'visible': capabilities['can_manage_daily_resources'],
                    'enabled': capabilities['can_manage_daily_resources'],
                    'disabled_reason': '' if capabilities['can_manage_daily_resources'] else 'Permissões de recursos do diário não concedidas',
                    'badge': '' ,
                    'order': 4,
                    'priority': 85,
                    'label': 'Recursos do Diário',
                    'icon': 'boxes',
                    'route': '/operacao/diario/recursos',
                },
                'production': {
                    'visible': capabilities['can_manage_production'],
                    'enabled': capabilities['can_manage_production'],
                    'disabled_reason': '' if capabilities['can_manage_production'] else 'Permissão de produção não concedida',
                    'badge': 'core' if capabilities['can_manage_production'] else '',
                    'order': 5,
                    'priority': 90,
                    'label': 'Produção',
                    'icon': 'factory',
                    'route': '/operacao/producao',
                },
            },
        },
        'visao_geral': {
            'visible': any([
                capabilities['can_view_operational_dashboard'],
                capabilities['can_view_reports'],
                capabilities['can_view_indicators'],
            ]),
            'order': 3,
            'priority': 95,
            'label': 'Visão Geral',
            'icon': 'layout-dashboard',
            'home_route': '/visao-geral',
            'items': {
                'dashboard': {
                    'visible': capabilities['can_view_operational_dashboard'],
                    'enabled': capabilities['can_view_operational_dashboard'],
                    'disabled_reason': '' if capabilities['can_view_operational_dashboard'] else 'Permissão de dashboard não concedida',
                    'badge': 'home' if capabilities['can_view_operational_dashboard'] else '',
                    'order': 1,
                    'priority': 100,
                    'label': 'Dashboard',
                    'icon': 'bar-chart-3',
                    'route': '/visao-geral/dashboard',
                },
                'reports': {
                    'visible': capabilities['can_view_reports'],
                    'enabled': capabilities['can_view_reports'],
                    'disabled_reason': '' if capabilities['can_view_reports'] else 'Permissão de relatórios não concedida',
                    'badge': '' ,
                    'order': 2,
                    'priority': 90,
                    'label': 'Relatórios',
                    'icon': 'file-bar-chart',
                    'route': '/visao-geral/relatorios',
                },
                'indicators': {
                    'visible': capabilities['can_view_indicators'],
                    'enabled': capabilities['can_view_indicators'],
                    'disabled_reason': '' if capabilities['can_view_indicators'] else 'Permissão de indicadores não concedida',
                    'badge': '' ,
                    'order': 3,
                    'priority': 85,
                    'label': 'Indicadores',
                    'icon': 'gauge',
                    'route': '/visao-geral/indicadores',
                },
            },
        },
        'governanca': {
            'visible': any([
                capabilities['can_manage_plans'],
                capabilities['can_manage_modules'],
                capabilities['can_manage_master_users'],
                capabilities['can_view_audit'],
            ]),
            'order': 4,
            'priority': 70,
            'label': 'Governança',
            'icon': 'landmark',
            'home_route': '/governanca',
            'items': {
                'plans': {
                    'visible': capabilities['can_manage_plans'],
                    'enabled': capabilities['can_manage_plans'],
                    'disabled_reason': '' if capabilities['can_manage_plans'] else 'Acesso restrito ao escopo master',
                    'badge': 'admin' if capabilities['can_manage_plans'] else '',
                    'order': 1,
                    'priority': 78,
                    'label': 'Planos',
                    'icon': 'layers-3',
                    'route': '/governanca/planos',
                },
                'modules': {
                    'visible': capabilities['can_manage_modules'],
                    'enabled': capabilities['can_manage_modules'],
                    'disabled_reason': '' if capabilities['can_manage_modules'] else 'Acesso restrito ao escopo master',
                    'badge': 'admin' if capabilities['can_manage_modules'] else '',
                    'order': 2,
                    'priority': 76,
                    'label': 'Módulos',
                    'icon': 'puzzle',
                    'route': '/governanca/modulos',
                },
                'master_users': {
                    'visible': capabilities['can_manage_master_users'],
                    'enabled': capabilities['can_manage_master_users'],
                    'disabled_reason': '' if capabilities['can_manage_master_users'] else 'Acesso restrito ao escopo master',
                    'badge': 'admin' if capabilities['can_manage_master_users'] else '',
                    'order': 3,
                    'priority': 74,
                    'label': 'Usuários Master',
                    'icon': 'user-cog',
                    'route': '/governanca/usuarios-master',
                },
                'audit': {
                    'visible': capabilities['can_view_audit'],
                    'enabled': capabilities['can_view_audit'],
                    'disabled_reason': '' if capabilities['can_view_audit'] else 'Permissão de auditoria não concedida',
                    'badge': 'log' if capabilities['can_view_audit'] else '',
                    'order': 4,
                    'priority': 82,
                    'label': 'Auditoria',
                    'icon': 'scroll-text',
                    'route': '/governanca/auditoria',
                },
            },
        },
    }


@app.route('/')
def root():
    return appConfig.apiInfo


@app.route('/api/v1/')
def main():
    return f'{appConfig.apiName} v.: {appConfig.apiVersion}'


@app.route('/api/v1/health')
def health():
    r = NXResult()
    r.status = True
    r.message = 'API ativa'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
    }
    return r.toJSON()


@app.route('/api/v1/ready')
def ready():
    r = master_database_ping()
    if r.status:
        validation = validate_master_database_config()
        r.data = {
            'database_ping': r.data,
            'database_config': validation,
        }
    return r.toJSON()


@app.route('/api/v1/routes')
def routes_catalog():
    r = NXResult()
    routes = []

    for rule in sorted(app.url_map.iter_rules(), key=lambda item: item.rule):
        if not rule.rule.startswith('/api/v1'):
            continue
        if rule.endpoint == 'static':
            continue

        methods = sorted([method for method in rule.methods if method not in {'HEAD', 'OPTIONS'}])
        routes.append(
            {
                'endpoint': rule.endpoint,
                'path': rule.rule,
                'methods': methods,
                'requires_token_path': '<token_id>' in rule.rule,
            }
        )

    r.status = True
    r.message = 'Catalogo de rotas carregado com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'total_routes': len(routes),
        'routes': routes,
    }
    return r.toJSON()


@app.route('/api/v1/smoke-plan')
def smoke_plan():
    r = NXResult()
    r.status = True
    r.message = 'Plano de smoke test carregado com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'references': {
            'doc': 'docs/api-smoke-test.md',
            'ready': '/api/v1/ready',
            'environment': '/api/v1/environment',
            'security_check': '/api/v1/security-check',
            'admin_bootstrap': '/api/v1/admin/bootstrap/<token_id>',
            'schema_compatibility': '/api/v1/admin/schema-compatibility/<token_id>',
        },
        'steps': [
            {
                'order': 1,
                'name': 'Runtime HTTP',
                'goal': 'Validar se a aplicacao sobe e responde.',
                'checks': [
                    {'method': 'GET', 'path': '/api/v1/health'},
                    {'method': 'GET', 'path': '/api/v1/ready'},
                    {'method': 'GET', 'path': '/api/v1/environment'},
                    {'method': 'GET', 'path': '/api/v1/routes'},
                ],
            },
            {
                'order': 2,
                'name': 'Master Schema',
                'goal': 'Validar compatibilidade minima do banco master.',
                'checks': [
                    {'method': 'POST', 'path': '/api/v1/auth/master/login/'},
                    {'method': 'GET', 'path': '/api/v1/admin/schema-compatibility/<token_id>'},
                    {'method': 'GET', 'path': '/api/v1/admin/bootstrap/<token_id>'},
                    {'method': 'POST', 'path': '/api/v1/admin/bootstrap/<token_id>'},
                ],
            },
            {
                'order': 3,
                'name': 'Tenant Bootstrap',
                'goal': 'Preparar o ambiente tenant inicial.',
                'checks': [
                    {'method': 'GET', 'path': '/api/v1/tenant/metadata/<token_id>'},
                    {'method': 'POST', 'path': '/api/v1/tenant/bootstrap/<token_id>'},
                    {'method': 'POST', 'path': '/api/v1/auth/tenant/login/'},
                ],
            },
            {
                'order': 4,
                'name': 'Operational Setup',
                'goal': 'Criar a primeira obra e estrutura operacional.',
                'checks': [
                    {'method': 'GET', 'path': '/api/v1/projects/<token_id>'},
                    {'method': 'POST', 'path': '/api/v1/projects/setup/<token_id>'},
                    {'method': 'GET', 'path': '/api/v1/teams/<token_id>'},
                    {'method': 'GET', 'path': '/api/v1/team_members/<token_id>'},
                ],
            },
            {
                'order': 5,
                'name': 'Diary Flow',
                'goal': 'Validar cadastro, consulta e acoes principais do diario.',
                'checks': [
                    {'method': 'GET', 'path': '/api/v1/diary/<token_id>'},
                    {'method': 'POST', 'path': '/api/v1/diary/<token_id>'},
                    {'method': 'GET', 'path': '/api/v1/diary/<diary_id>/<token_id>'},
                    {'method': 'GET', 'path': '/api/v1/diary/<diary_id>/export/<token_id>'},
                ],
            },
            {
                'order': 6,
                'name': 'Production Flow',
                'goal': 'Validar cadastro e consulta de producao.',
                'checks': [
                    {'method': 'GET', 'path': '/api/v1/production/<token_id>'},
                    {'method': 'POST', 'path': '/api/v1/production/<token_id>'},
                ],
            },
            {
                'order': 7,
                'name': 'Reports And Audit',
                'goal': 'Validar visao gerencial e observabilidade.',
                'checks': [
                    {'method': 'GET', 'path': '/api/v1/dashboard/operational/<token_id>'},
                    {'method': 'GET', 'path': '/api/v1/reports/projects/summary/<token_id>'},
                    {'method': 'GET', 'path': '/api/v1/audit/logs/<token_id>'},
                ],
            },
            {
                'order': 8,
                'name': 'Security Check',
                'goal': 'Sinalizar configuracoes basicas de risco antes do deploy.',
                'checks': [
                    {'method': 'GET', 'path': '/api/v1/security-check'},
                ],
            },
        ],
    }
    return r.toJSON()


@app.route('/api/v1/security-check')
def security_check():
    r = NXResult()
    warnings = []
    checks = {
        'secret_key_changed': appConfig.secretKey != 'change-me',
        'database_ssl_required': appConfig.dbSslMode == 'require' or 'sslmode=require' in build_connection_string().lower(),
        'database_password_configured': bool(appConfig.dbPassword),
        'default_local_user': appConfig.dbUser != 'postgres' or appConfig.dbHost not in {'localhost', '127.0.0.1'},
    }

    if not checks['secret_key_changed']:
        warnings.append('OBRAX_SECRET_KEY ainda esta com valor padrao')
    if not checks['database_ssl_required']:
        warnings.append('Conexao principal nao esta com sslmode=require')
    if not checks['database_password_configured']:
        warnings.append('Senha do banco principal nao foi configurada')
    if not checks['default_local_user']:
        warnings.append('Configuracao ainda parece ambiente local padrao com usuario postgres')

    r.status = True
    r.message = 'Checklist de seguranca carregado com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'safe': len(warnings) == 0,
        'checks': checks,
        'warnings': warnings,
    }
    return r.toJSON()


@app.route('/api/v1/conventions')
def conventions():
    r = NXResult()
    r.status = True
    r.message = 'Convencoes da API carregadas com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'response_pattern': 'NXResult',
        'response_example': {
            'nx_result': True,
            'status': True,
            'code': -1,
            'info': False,
            'warning': False,
            'error': False,
            'message': 'Operacao realizada com sucesso',
            'error_msg': '',
            'data': {},
        },
        'authentication': {
            'master_login': {
                'method': 'POST',
                'path': '/api/v1/auth/master/login/',
                'body': ['login', 'password'],
            },
            'tenant_login': {
                'method': 'POST',
                'path': '/api/v1/auth/tenant/login/',
                'headers': ['X-Account-Code'],
                'body': ['email', 'password'],
            },
            'token_transport': {
                'type': 'path',
                'placeholder': '<token_id>',
                'example': '/api/v1/projects/<token_id>',
            },
        },
        'headers': {
            'tenant_login_required': ['X-Account-Code'],
            'general_supported': [
                'Origin',
                'Content-Type',
                'Authorization',
                'X-Auth-Token',
                'X-Account-Code',
            ],
        },
        'common_query_params': {
            'diary': ['project_id', 'status', 'created_by', 'start_date', 'end_date'],
            'production': ['project_id', 'created_by', 'start_date', 'end_date'],
            'audit': ['module', 'action', 'table_name', 'record_id', 'start_date', 'end_date', 'limit', 'offset'],
            'reports': ['project_id', 'start_date', 'end_date'],
        },
        'message_patterns': {
            'create': '... cadastrado com sucesso',
            'update': '... atualizado com sucesso',
            'delete': '... excluido com sucesso',
            'bootstrap': '... executado com sucesso',
            'validation_error': 'Dados invalidos enviados',
            'runtime_error': 'Erro ao processar ...',
        },
        'payload_reference': '/api/v1/payloads',
        'examples_reference': '/api/v1/examples',
        'queries_reference': '/api/v1/queries',
        'responses_reference': '/api/v1/responses',
        'catalog_reference': '/api/v1/catalog',
        'recommended_aliases': {
            'diary_detail': '/api/v1/diary/<diary_id>/<token_id>',
            'diary_export': '/api/v1/diary/<diary_id>/export/<token_id>',
            'diary_approve': '/api/v1/diary/<diary_id>/approve/<token_id>',
            'diary_reject': '/api/v1/diary/<diary_id>/reject/<token_id>',
            'report_project_diaries': '/api/v1/reports/projects/diaries/<token_id>',
            'report_project_summary': '/api/v1/reports/projects/summary/<token_id>',
            'audit_project_timeline': '/api/v1/audit/projects/timeline/<token_id>',
            'audit_diary_timeline': '/api/v1/audit/diaries/timeline/<token_id>',
            'dashboard_user_summary': '/api/v1/dashboard/users/summary/<token_id>',
        },
    }
    return r.toJSON()


@app.route('/api/v1/environment')
def environment():
    r = NXResult()
    connection_string = build_connection_string()
    validation = validate_master_database_config()
    r.status = True
    r.message = 'Manifesto de ambiente carregado com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'python_runtime': 'python-3.12.8',
        'database': {
            'uses_database_url': bool(appConfig.databaseUrl),
            'host': appConfig.dbHost,
            'port': appConfig.dbPort,
            'name': appConfig.dbName,
            'user': appConfig.dbUser,
            'sslmode': appConfig.dbSslMode,
            'password_configured': bool(appConfig.dbPassword),
            'connection_string_present': bool(connection_string),
            'validation': validation,
        },
        'security': {
            'secret_key_configured': appConfig.secretKey != 'change-me',
        },
    }
    return r.toJSON()


@app.route('/api/v1/about')
def about():
    r = NXResult()
    r.status = True
    r.message = 'Resumo da API carregado com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'pattern': 'source',
        'response_pattern': 'NXResult',
        'entrypoints': {
            'root': '/',
            'api': '/api/v1/',
            'health': '/api/v1/health',
            'ready': '/api/v1/ready',
            'routes': '/api/v1/routes',
            'conventions': '/api/v1/conventions',
            'environment': '/api/v1/environment',
            'payloads': '/api/v1/payloads',
            'examples': '/api/v1/examples',
            'queries': '/api/v1/queries',
            'responses': '/api/v1/responses',
            'catalog': '/api/v1/catalog',
            'capabilities': '/api/v1/capabilities/<token_id>',
            'feature_map': '/api/v1/feature-map/<token_id>',
            'context_actions': '/api/v1/context-actions/<entity>/<record_id>/<token_id>',
            'screen_context': '/api/v1/screen-context/<token_id>',
            'screen_context_record': '/api/v1/screen-context/<entity>/<record_id>/<token_id>',
        },
        'authentication': {
            'master_login': '/api/v1/auth/master/login/',
            'tenant_login': '/api/v1/auth/tenant/login/',
            'tenant_header_required': 'X-Account-Code',
            'authenticated_path_token': '<token_id>',
        },
        'modules': [
            'admin',
            'tenant',
            'projects',
            'teams',
            'diary',
            'production',
            'reports',
            'audit',
            'dashboard',
            'indicators',
        ],
        'recommended_first_steps': [
            'GET /api/v1/health',
            'GET /api/v1/ready',
            'POST /api/v1/auth/master/login/',
            'POST /api/v1/auth/tenant/login/',
            'POST /api/v1/tenant/bootstrap/<token_id>',
            'POST /api/v1/projects/setup/<token_id>',
        ],
    }
    return r.toJSON()


@app.route('/api/v1/catalog')
def catalog():
    r = NXResult()
    r.status = True
    r.message = 'Catalogo modular da API carregado com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'modules': _build_module_catalog(),
        'notes': [
            'Capabilities representam a intencao funcional de cada modulo.',
            'Permissions representam os codigos sugeridos para controle de acesso no frontend e backend.',
        ],
    }
    return r.toJSON()


@app.route('/api/v1/catalog/<token_id>')
def catalog_by_token(token_id):
    r = NXResult()
    nx = NXConnection()

    try:
        login_type = _resolve_login_type_by_token(token_id)
        r = nx.login(login_type, token_id)
        if r.status is True:
            resolved_catalog = _resolve_catalog_for_session(nx.session.scope, nx.session.permissions)
            r.status = True
            r.message = 'Catalogo resolvido por autenticacao carregado com sucesso'
            r.data = {
                'name': appConfig.apiName,
                'version': appConfig.apiVersion,
                'scope': nx.session.scope,
                'user_id': nx.session.userid,
                'account_code': nx.session.account_code,
                'permissions': nx.session.permissions,
                'modules': resolved_catalog,
            }
    except Exception as e:
        r.make_error(0, 'Erro ao carregar catalogo resolvido', str(e))
    finally:
        nx.stop()

    return r.toJSON()


@app.route('/api/v1/session/<token_id>')
def session_by_token(token_id):
    r = NXResult()
    nx = NXConnection()

    try:
        login_type = _resolve_login_type_by_token(token_id)
        r = nx.login(login_type, token_id)
        if r.status is True:
            resolved_catalog = _resolve_catalog_for_session(nx.session.scope, nx.session.permissions)
            r.status = True
            r.message = 'Sessao autenticada carregada com sucesso'
            r.data = {
                'name': appConfig.apiName,
                'version': appConfig.apiVersion,
                'session': {
                    'user_id': nx.session.userid,
                    'scope': nx.session.scope,
                    'account_code': nx.session.account_code,
                    'permissions': nx.session.permissions,
                    'visible_modules': _visible_modules(resolved_catalog),
                },
            }
    except Exception as e:
        r.make_error(0, 'Erro ao carregar sessao autenticada', str(e))
    finally:
        nx.stop()

    return r.toJSON()


@app.route('/api/v1/capabilities/<token_id>')
def capabilities_by_token(token_id):
    r = NXResult()
    nx = NXConnection()

    try:
        login_type = _resolve_login_type_by_token(token_id)
        r = nx.login(login_type, token_id)
        if r.status is True:
            resolved_catalog = _resolve_catalog_for_session(nx.session.scope, nx.session.permissions)
            r.status = True
            r.message = 'Capabilities da sessao carregadas com sucesso'
            r.data = {
                'name': appConfig.apiName,
                'version': appConfig.apiVersion,
                'scope': nx.session.scope,
                'permissions': nx.session.permissions,
                'visible_modules': _visible_modules(resolved_catalog),
                'capabilities': _resolved_capabilities(nx.session.scope, nx.session.permissions),
            }
    except Exception as e:
        r.make_error(0, 'Erro ao carregar capabilities da sessao', str(e))
    finally:
        nx.stop()

    return r.toJSON()


@app.route('/api/v1/feature-map/<token_id>')
def feature_map_by_token(token_id):
    r = NXResult()
    nx = NXConnection()

    try:
        login_type = _resolve_login_type_by_token(token_id)
        r = nx.login(login_type, token_id)
        if r.status is True:
            resolved_catalog = _resolve_catalog_for_session(nx.session.scope, nx.session.permissions)
            r.status = True
            r.message = 'Mapa de funcionalidades da sessao carregado com sucesso'
            r.data = {
                'name': appConfig.apiName,
                'version': appConfig.apiVersion,
                'scope': nx.session.scope,
                'mode': 'master' if nx.session.scope == 'master' else 'tenant',
                'visible_modules': _visible_modules(resolved_catalog),
                'feature_map': _feature_map(nx.session.scope, nx.session.permissions),
            }
    except Exception as e:
        r.make_error(0, 'Erro ao carregar mapa de funcionalidades da sessao', str(e))
    finally:
        nx.stop()

    return r.toJSON()


@app.route('/api/v1/context-actions/<entity>/<int:record_id>/<token_id>')
def context_actions_by_record(entity, record_id, token_id):
    r = NXResult()
    nx = NXConnection()

    try:
        login_type = _resolve_login_type_by_token(token_id)
        r = nx.login(login_type, token_id)
        if r.status is True:
            if entity == 'diary':
                loaded, record = load_diary_record(nx, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _diary_context_actions(nx.session.scope, nx.session.permissions, record)
            elif entity == 'project':
                loaded, record = load_project_record(nx, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _project_context_actions(nx.session.scope, nx.session.permissions, record)
            elif entity == 'production':
                loaded, record = load_production_record(nx, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _production_context_actions(nx.session.scope, nx.session.permissions, record)
            elif entity == 'team':
                loaded, record = load_team_record(nx, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _team_context_actions(nx.session.scope, nx.session.permissions, record)
            elif entity == 'team_member':
                loaded, record = load_generic_record(nx, SQL_TEAM_MEMBER_BY_ID, record_id, 'Membro da equipe nao localizado', 'Erro ao consultar membro da equipe')
                if loaded.error:
                    return loaded.toJSON()
                payload = _team_member_context_actions(nx.session.scope, nx.session.permissions, record)
            elif entity == 'occurrence':
                loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_OCCURRENCE_BY_ID, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'occurrence', record_id, diary_id)
            elif entity == 'activity':
                loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_ACTIVITY_BY_ID, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'activity', record_id, diary_id)
            elif entity == 'labor':
                loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_LABOR_BY_ID, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'labor', record_id, diary_id)
            elif entity == 'material':
                loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_MATERIAL_BY_ID, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'material', record_id, diary_id)
            elif entity == 'equipment':
                loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_EQUIPMENT_BY_ID, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'equipment', record_id, diary_id)
            elif entity == 'file':
                loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_FILE_BY_ID, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'file', record_id, diary_id)
            elif entity == 'signature':
                loaded, diary_id = load_aux_daily_log_id(nx, SQL_DAILY_SIGNATURE_BY_ID, record_id)
                if loaded.error:
                    return loaded.toJSON()
                payload = _daily_resource_context_actions(nx.session.scope, nx.session.permissions, 'signature', record_id, diary_id)
            else:
                r.make_error(0, 'Entidade de contexto nao suportada')
                return r.toJSON()

            r.status = True
            r.message = 'Acoes contextuais carregadas com sucesso'
            r.data = {
                'name': appConfig.apiName,
                'version': appConfig.apiVersion,
                'scope': nx.session.scope,
                'context': payload,
            }
    except Exception as e:
        r.make_error(0, 'Erro ao carregar acoes contextuais', str(e))
    finally:
        nx.stop()

    return r.toJSON()


@app.route('/api/v1/screen-context/<token_id>')
def screen_context(token_id):
    r = NXResult()
    nx = NXConnection()

    try:
        login_type = _resolve_login_type_by_token(token_id)
        r = nx.login(login_type, token_id)
        if r.status is True:
            r.status = True
            r.message = 'Contexto de tela carregado com sucesso'
            r.data = _screen_context_payload(nx)
    except Exception as e:
        r.make_error(0, 'Erro ao carregar contexto de tela', str(e))
    finally:
        nx.stop()

    return r.toJSON()


@app.route('/api/v1/screen-context/<entity>/<int:record_id>/<token_id>')
def screen_context_by_record(entity, record_id, token_id):
    r = NXResult()
    nx = NXConnection()

    try:
        login_type = _resolve_login_type_by_token(token_id)
        r = nx.login(login_type, token_id)
        if r.status is True:
            payload = _screen_context_payload(nx, entity, record_id)
            if 'error' in payload:
                return payload['error']
            r.status = True
            r.message = 'Contexto de tela por registro carregado com sucesso'
            r.data = payload
    except Exception as e:
        r.make_error(0, 'Erro ao carregar contexto de tela por registro', str(e))
    finally:
        nx.stop()

    return r.toJSON()


@app.route('/api/v1/queries')
def queries():
    r = NXResult()
    r.status = True
    r.message = 'Queries da API carregadas com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'queries': _api_query_reference(),
        'notes': [
            'Query params podem ser opcionais conforme a rota.',
            'Filtros de periodo usam o padrao YYYY-MM-DD.',
        ],
    }
    return r.toJSON()


@app.route('/api/v1/payloads')
def payloads():
    r = NXResult()
    r.status = True
    r.message = 'Payloads da API carregados com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'payloads': {
            'admin.accounts.create': {
                'required_fields': ['code', 'name'],
                'optional_fields': [
                    'document',
                    'phone',
                    'email',
                    'status',
                    'plan_id',
                    'database_url',
                    'database_host',
                    'database_port',
                    'database_name',
                    'database_user',
                    'database_password',
                    'database_sslmode',
                    'storage_limit_mb',
                    'storage_used_mb',
                    'expiration_date',
                    'active',
                ],
            },
            'admin.plans.create': {
                'required_fields': ['name'],
                'optional_fields': [
                    'description',
                    'price',
                    'max_companies',
                    'max_users',
                    'max_works',
                    'max_storage_mb',
                    'active',
                ],
            },
            'admin.modules.create': {
                'required_fields': ['code', 'name'],
                'optional_fields': ['description', 'active'],
            },
            'admin.account_modules.create': {
                'required_fields': ['account_id', 'module_id'],
                'optional_fields': ['active'],
            },
            'admin.master_users.create': {
                'required_fields': ['name', 'login', 'password'],
                'optional_fields': ['email', 'phone', 'role', 'active'],
            },
            'auth.master_login': {
                'required_fields': ['login', 'password'],
                'optional_fields': [],
            },
            'auth.tenant_login': {
                'required_headers': ['X-Account-Code'],
                'required_fields': ['email', 'password'],
                'optional_fields': [],
            },
            'tenant.companies.create': {
                'required_fields': ['code', 'document', 'corporate_name'],
                'optional_fields': [
                    'fantasy_name',
                    'phone',
                    'email',
                    'zipcode',
                    'address',
                    'number',
                    'district',
                    'city',
                    'state',
                    'active',
                ],
            },
            'tenant.roles.create': {
                'required_fields': ['name'],
                'optional_fields': ['description', 'active'],
            },
            'tenant.permissions.create': {
                'required_fields': ['code', 'name'],
                'optional_fields': ['description', 'module_name', 'active'],
            },
            'tenant.role_permissions.create': {
                'required_fields': ['role_id', 'permission_id'],
                'optional_fields': [],
            },
            'tenant.users.create': {
                'required_fields': ['company_id', 'name', 'email', 'password'],
                'optional_fields': ['role_id', 'phone', 'active'],
            },
            'tenant.bootstrap': {
                'required_fields': [
                    'company_code',
                    'company_document',
                    'corporate_name',
                    'admin_name',
                    'admin_email',
                    'admin_password',
                ],
                'optional_fields': [
                    'fantasy_name',
                    'phone',
                    'email',
                    'zipcode',
                    'address',
                    'number',
                    'district',
                    'city',
                    'state',
                ],
            },
            'projects.setup': {
                'required_fields': [
                    'project_name',
                    'project_code',
                    'company_id',
                    'main_team_name',
                ],
                'optional_fields': [
                    'client_name',
                    'engineer_user_id',
                    'address',
                    'number',
                    'district',
                    'city',
                    'state',
                    'zipcode',
                    'budget_amount',
                    'status',
                    'main_team_description',
                    'members',
                ],
            },
            'projects.create': {
                'required_fields': ['company_id', 'project_code', 'project_name'],
                'optional_fields': [
                    'client_name',
                    'engineer_user_id',
                    'address',
                    'number',
                    'district',
                    'city',
                    'state',
                    'zipcode',
                    'budget_amount',
                    'status',
                ],
            },
            'projects.update': {
                'required_fields': ['id'],
                'optional_fields': [
                    'company_id',
                    'project_code',
                    'project_name',
                    'client_name',
                    'engineer_user_id',
                    'address',
                    'number',
                    'district',
                    'city',
                    'state',
                    'zipcode',
                    'budget_amount',
                    'status',
                ],
            },
            'teams.create': {
                'required_fields': ['project_id', 'team_name'],
                'optional_fields': ['description', 'active'],
            },
            'teams.update': {
                'required_fields': ['id'],
                'optional_fields': ['project_id', 'team_name', 'description', 'active'],
            },
            'team_members.create': {
                'required_fields': ['team_id', 'member_name'],
                'optional_fields': ['user_id', 'role_name', 'active'],
            },
            'team_members.update': {
                'required_fields': ['id'],
                'optional_fields': ['team_id', 'user_id', 'member_name', 'role_name', 'active'],
            },
            'diary.create': {
                'required_fields': ['project_id', 'work_date'],
                'optional_fields': ['weather', 'summary', 'occurrences', 'status', 'created_by'],
            },
            'diary.update': {
                'required_fields': ['id'],
                'optional_fields': ['project_id', 'work_date', 'weather', 'summary', 'occurrences', 'status'],
            },
            'production.create': {
                'required_fields': ['project_id', 'reference_date', 'service_name'],
                'optional_fields': ['unit', 'planned_quantity', 'executed_quantity', 'notes', 'created_by'],
            },
            'production.update': {
                'required_fields': ['id'],
                'optional_fields': [
                    'project_id',
                    'reference_date',
                    'service_name',
                    'unit',
                    'planned_quantity',
                    'executed_quantity',
                    'notes',
                ],
            },
            'daily.occurrences.create': {
                'required_fields': ['daily_log_id', 'description'],
                'optional_fields': ['occurrence_type', 'resolved'],
            },
            'daily.occurrences.update': {
                'required_fields': ['id'],
                'optional_fields': ['description', 'occurrence_type', 'resolved'],
            },
            'daily.activities.create': {
                'required_fields': ['daily_log_id', 'description'],
                'optional_fields': ['sector_name', 'quantity_executed', 'unit'],
            },
            'daily.activities.update': {
                'required_fields': ['id'],
                'optional_fields': ['description', 'sector_name', 'quantity_executed', 'unit'],
            },
            'daily.labor.create': {
                'required_fields': ['daily_log_id', 'role_name'],
                'optional_fields': ['team_id', 'worker_count', 'worked_hours'],
            },
            'daily.labor.update': {
                'required_fields': ['id'],
                'optional_fields': ['team_id', 'role_name', 'worker_count', 'worked_hours'],
            },
            'daily.materials.create': {
                'required_fields': ['daily_log_id', 'material_name'],
                'optional_fields': ['unit', 'quantity', 'notes'],
            },
            'daily.materials.update': {
                'required_fields': ['id'],
                'optional_fields': ['material_name', 'unit', 'quantity', 'notes'],
            },
            'daily.equipments.create': {
                'required_fields': ['daily_log_id', 'equipment_name'],
                'optional_fields': ['quantity', 'worked_hours', 'notes'],
            },
            'daily.equipments.update': {
                'required_fields': ['id'],
                'optional_fields': ['equipment_name', 'quantity', 'worked_hours', 'notes'],
            },
            'daily.files.create': {
                'required_fields': ['daily_log_id', 'file_name'],
                'optional_fields': ['file_url', 'file_type'],
            },
            'daily.files.update': {
                'required_fields': ['id'],
                'optional_fields': ['file_name', 'file_url', 'file_type'],
            },
            'daily.signatures.create': {
                'required_fields': ['daily_log_id', 'signed_by_name'],
                'optional_fields': ['signed_by_user_id', 'signature_type'],
            },
            'daily.signatures.update': {
                'required_fields': ['id'],
                'optional_fields': ['signed_by_user_id', 'signed_by_name', 'signature_type'],
            },
        },
        'notes': [
            'Campos opcionais podem variar conforme regra de negocio e permissao do tenant.',
            'Use /api/v1/examples para exemplos completos de body por fluxo.',
        ],
    }
    return r.toJSON()


@app.route('/api/v1/examples')
def examples():
    r = NXResult()
    r.status = True
    r.message = 'Exemplos da API carregados com sucesso'
    r.data = _api_examples()
    return r.toJSON()


@app.route('/api/v1/responses')
def responses():
    r = NXResult()
    r.status = True
    r.message = 'Exemplos de resposta da API carregados com sucesso'
    r.data = {
        'name': appConfig.apiName,
        'version': appConfig.apiVersion,
        'response_pattern': 'NXResult',
        'responses': _api_response_examples(),
    }
    return r.toJSON()

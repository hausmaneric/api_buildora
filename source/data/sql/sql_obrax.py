SQL_LOGIN = """
SELECT id,
       name,
       email,
       password_hash,
       role,
       active
  FROM users
 WHERE email = %s
 LIMIT 1
"""

SQL_DIARY_LIST = """
SELECT id,
       project_id,
       work_date,
       weather,
       summary,
       status,
       created_at,
       updated_at
  FROM daily_logs
 WHERE (%s IS NULL OR project_id = %s)
 ORDER BY work_date DESC, id DESC
"""

SQL_DIARY_INSERT = """
INSERT INTO daily_logs (
    project_id,
    work_date,
    weather,
    summary,
    occurrences,
    status,
    created_by
) VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DIARY_BY_ID = """
SELECT id,
       project_id,
       work_date,
       weather,
       summary,
       occurrences,
       status,
       created_by,
       created_at,
       updated_at
  FROM daily_logs
 WHERE id = %s
 LIMIT 1
"""

SQL_DIARY_UPDATE = """
UPDATE daily_logs
   SET weather = %s,
       summary = %s,
       occurrences = %s,
       status = %s,
       updated_at = NOW()
 WHERE id = %s
RETURNING id, status
"""

SQL_DIARY_STATUS_UPDATE = """
UPDATE daily_logs
   SET status = %s,
       updated_at = NOW()
 WHERE id = %s
RETURNING id, status
"""

SQL_PRODUCTION_LIST = """
SELECT id,
       project_id,
       reference_date,
       service_name,
       unit,
       planned_quantity,
       executed_quantity,
       notes,
       created_at,
       updated_at
  FROM production_entries
 WHERE (%s IS NULL OR project_id = %s)
 ORDER BY reference_date DESC, id DESC
"""

SQL_PRODUCTION_INSERT = """
INSERT INTO production_entries (
    project_id,
    reference_date,
    service_name,
    unit,
    planned_quantity,
    executed_quantity,
    notes,
    created_by
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_PRODUCTION_BY_ID = """
SELECT id,
       project_id,
       reference_date,
       service_name,
       unit,
       planned_quantity,
       executed_quantity,
       notes,
       created_by,
       created_at,
       updated_at
  FROM production_entries
 WHERE id = %s
 LIMIT 1
"""

SQL_PRODUCTION_UPDATE = """
UPDATE production_entries
   SET project_id = %s,
       reference_date = %s,
       service_name = %s,
       unit = %s,
       planned_quantity = %s,
       executed_quantity = %s,
       notes = %s,
       updated_at = NOW()
 WHERE id = %s
RETURNING id
"""

SQL_PRODUCTION_DELETE = """
DELETE FROM production_entries
 WHERE id = %s
RETURNING id
"""

SQL_ACCOUNT_BY_CODE = """
SELECT id,
       code,
       name,
       document,
       phone,
       email,
       status,
       plan_id,
       database_url,
       database_host,
       database_port,
       database_name,
       database_user,
       database_password,
       database_sslmode,
       storage_limit_mb,
       storage_used_mb,
       expiration_date,
       active
  FROM accounts
 WHERE code = %s
   AND active = TRUE
 LIMIT 1
"""

SQL_DATABASE_METADATA_UPSERT = """
INSERT INTO database_metadata (
    metadata_key,
    metadata_value,
    updated_at
) VALUES (%s, %s, NOW())
ON CONFLICT (metadata_key)
DO UPDATE SET metadata_value = EXCLUDED.metadata_value,
              updated_at = NOW()
RETURNING id, metadata_key, metadata_value, updated_at
"""

SQL_DATABASE_METADATA_BY_KEY = """
SELECT id,
       metadata_key,
       metadata_value,
       updated_at
  FROM database_metadata
 WHERE metadata_key = %s
 LIMIT 1
"""

SQL_MASTER_PLAN_BY_NAME = """
SELECT id,
       name,
       active
  FROM plans
 WHERE name = %s
 LIMIT 1
"""

SQL_MASTER_MODULE_BY_CODE = """
SELECT id,
       code,
       name,
       active
  FROM modules
 WHERE code = %s
 LIMIT 1
"""

SQL_MASTER_USER_BY_LOGIN = """
SELECT id,
       name,
       login,
       active
  FROM master_users
 WHERE login = %s
 LIMIT 1
"""

SQL_TABLE_EXISTS = """
SELECT EXISTS (
    SELECT 1
      FROM information_schema.tables
     WHERE table_schema = 'public'
       AND table_name = %s
) AS exists_flag
"""

SQL_MASTER_ACCOUNTS_LIST = """
SELECT id,
       code,
       name,
       document,
       email,
       phone,
       status,
       plan_id,
       storage_limit_mb,
       storage_used_mb,
       expiration_date,
       active
  FROM accounts
 ORDER BY id DESC
"""

SQL_MASTER_ACCOUNTS_LIST_PAGED = """
SELECT id,
       code,
       name,
       document,
       email,
       phone,
       status,
       plan_id,
       storage_limit_mb,
       storage_used_mb,
       expiration_date,
       active
  FROM accounts
 WHERE (%s = '' OR code ILIKE %s OR name ILIKE %s OR email ILIKE %s OR document ILIKE %s)
 ORDER BY
   CASE WHEN %s = 'code' AND %s = 'asc' THEN code END ASC,
   CASE WHEN %s = 'code' AND %s = 'desc' THEN code END DESC,
   CASE WHEN %s = 'name' AND %s = 'asc' THEN name END ASC,
   CASE WHEN %s = 'name' AND %s = 'desc' THEN name END DESC,
   CASE WHEN %s = 'email' AND %s = 'asc' THEN email END ASC,
   CASE WHEN %s = 'email' AND %s = 'desc' THEN email END DESC,
   id DESC
 LIMIT %s OFFSET %s
"""

SQL_MASTER_ACCOUNTS_COUNT = """
SELECT COUNT(*) AS total
  FROM accounts
 WHERE (%s = '' OR code ILIKE %s OR name ILIKE %s OR email ILIKE %s OR document ILIKE %s)
"""

SQL_MASTER_ACCOUNT_INSERT = """
INSERT INTO accounts (
    code,
    name,
    document,
    phone,
    email,
    status,
    plan_id,
    database_url,
    database_host,
    database_port,
    database_name,
    database_user,
    database_password,
    database_sslmode,
    storage_limit_mb,
    storage_used_mb,
    expiration_date,
    active
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id, code
"""

SQL_MASTER_ACCOUNT_BY_ID = """
SELECT id,
       code,
       name,
       document,
       phone,
       email,
       status,
       plan_id,
       database_url,
       database_host,
       database_port,
       database_name,
       database_user,
       database_password,
       database_sslmode,
       storage_limit_mb,
       storage_used_mb,
       expiration_date,
       active
  FROM accounts
 WHERE id = %s
 LIMIT 1
"""

SQL_MASTER_ACCOUNT_UPDATE = """
UPDATE accounts
   SET code = %s,
       name = %s,
       document = %s,
       phone = %s,
       email = %s,
       status = %s,
       plan_id = %s,
       database_url = %s,
       database_host = %s,
       database_port = %s,
       database_name = %s,
       database_user = %s,
       database_password = %s,
       database_sslmode = %s,
       storage_limit_mb = %s,
       storage_used_mb = %s,
       expiration_date = %s,
       active = %s,
       updated_at = NOW()
 WHERE id = %s
RETURNING id, code
"""

SQL_MASTER_ACCOUNT_DELETE = """
DELETE FROM accounts
 WHERE id = %s
RETURNING id
"""

SQL_MASTER_PLANS_LIST = """
SELECT id,
       name,
       description,
       price,
       max_companies,
       max_users,
       max_works,
       max_storage_mb,
       active
  FROM plans
 ORDER BY id DESC
"""

SQL_MASTER_PLANS_LIST_PAGED = """
SELECT id,
       name,
       description,
       price,
       max_companies,
       max_users,
       max_works,
       max_storage_mb,
       active
  FROM plans
 WHERE (%s = '' OR name ILIKE %s OR description ILIKE %s OR name ILIKE %s OR description ILIKE %s)
 ORDER BY
   CASE WHEN %s = 'name' AND %s = 'asc' THEN name END ASC,
   CASE WHEN %s = 'name' AND %s = 'desc' THEN name END DESC,
   CASE WHEN %s = 'price' AND %s = 'asc' THEN price END ASC,
   CASE WHEN %s = 'price' AND %s = 'desc' THEN price END DESC,
   id DESC
 LIMIT %s OFFSET %s
"""

SQL_MASTER_PLANS_COUNT = """
SELECT COUNT(*) AS total
  FROM plans
 WHERE (%s = '' OR name ILIKE %s OR description ILIKE %s OR name ILIKE %s OR description ILIKE %s)
"""

SQL_MASTER_PLAN_INSERT = """
INSERT INTO plans (
    name,
    description,
    price,
    max_companies,
    max_users,
    max_works,
    max_storage_mb,
    active
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_MASTER_PLAN_BY_ID = """
SELECT id,
       name,
       description,
       price,
       max_companies,
       max_users,
       max_works,
       max_storage_mb,
       active
  FROM plans
 WHERE id = %s
 LIMIT 1
"""

SQL_MASTER_PLAN_UPDATE = """
UPDATE plans
   SET name = %s,
       description = %s,
       price = %s,
       max_companies = %s,
       max_users = %s,
       max_works = %s,
       max_storage_mb = %s,
       active = %s
 WHERE id = %s
RETURNING id
"""

SQL_MASTER_PLAN_DELETE = """
DELETE FROM plans
 WHERE id = %s
RETURNING id
"""

SQL_MASTER_MODULES_LIST = """
SELECT id,
       code,
       name,
       description,
       active
  FROM modules
 ORDER BY id DESC
"""

SQL_MASTER_MODULES_LIST_PAGED = """
SELECT id,
       code,
       name,
       description,
       active
  FROM modules
 WHERE (%s = '' OR code ILIKE %s OR name ILIKE %s OR description ILIKE %s OR code ILIKE %s)
 ORDER BY
   CASE WHEN %s = 'code' AND %s = 'asc' THEN code END ASC,
   CASE WHEN %s = 'code' AND %s = 'desc' THEN code END DESC,
   CASE WHEN %s = 'name' AND %s = 'asc' THEN name END ASC,
   CASE WHEN %s = 'name' AND %s = 'desc' THEN name END DESC,
   id DESC
 LIMIT %s OFFSET %s
"""

SQL_MASTER_MODULES_COUNT = """
SELECT COUNT(*) AS total
  FROM modules
 WHERE (%s = '' OR code ILIKE %s OR name ILIKE %s OR description ILIKE %s OR code ILIKE %s)
"""

SQL_MASTER_MODULE_INSERT = """
INSERT INTO modules (
    code,
    name,
    description,
    active
) VALUES (%s, %s, %s, %s)
RETURNING id
"""

SQL_MASTER_MODULE_BY_ID = """
SELECT id,
       code,
       name,
       description,
       active
  FROM modules
 WHERE id = %s
 LIMIT 1
"""

SQL_MASTER_MODULE_UPDATE = """
UPDATE modules
   SET code = %s,
       name = %s,
       description = %s,
       active = %s
 WHERE id = %s
RETURNING id
"""

SQL_MASTER_MODULE_DELETE = """
DELETE FROM modules
 WHERE id = %s
RETURNING id
"""

SQL_MASTER_USERS_LIST = """
SELECT id,
       name,
       login,
       email,
       phone,
       role,
       active
  FROM master_users
 ORDER BY id DESC
"""

SQL_MASTER_USERS_LIST_PAGED = """
SELECT id,
       name,
       login,
       email,
       phone,
       role,
       active
  FROM master_users
 WHERE (%s = '' OR name ILIKE %s OR login ILIKE %s OR email ILIKE %s OR role ILIKE %s)
 ORDER BY
   CASE WHEN %s = 'name' AND %s = 'asc' THEN name END ASC,
   CASE WHEN %s = 'name' AND %s = 'desc' THEN name END DESC,
   CASE WHEN %s = 'login' AND %s = 'asc' THEN login END ASC,
   CASE WHEN %s = 'login' AND %s = 'desc' THEN login END DESC,
   id DESC
 LIMIT %s OFFSET %s
"""

SQL_MASTER_USERS_COUNT = """
SELECT COUNT(*) AS total
  FROM master_users
 WHERE (%s = '' OR name ILIKE %s OR login ILIKE %s OR email ILIKE %s OR role ILIKE %s)
"""

SQL_MASTER_USER_INSERT = """
INSERT INTO master_users (
    name,
    login,
    password_hash,
    email,
    phone,
    role,
    active
) VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_MASTER_USER_BY_ID = """
SELECT id,
       name,
       login,
       email,
       phone,
       role,
       active
  FROM master_users
 WHERE id = %s
 LIMIT 1
"""

SQL_MASTER_USER_UPDATE = """
UPDATE master_users
   SET name = %s,
       login = %s,
       email = %s,
       phone = %s,
       role = %s,
       active = %s
 WHERE id = %s
RETURNING id
"""

SQL_MASTER_USER_UPDATE_WITH_PASSWORD = """
UPDATE master_users
   SET name = %s,
       login = %s,
       password_hash = %s,
       email = %s,
       phone = %s,
       role = %s,
       active = %s
 WHERE id = %s
RETURNING id
"""

SQL_MASTER_USER_DELETE = """
DELETE FROM master_users
 WHERE id = %s
RETURNING id
"""

SQL_MASTER_LOGIN = """
SELECT id,
       name,
       login,
       password_hash,
       email,
       role,
       active
  FROM master_users
 WHERE login = %s
 LIMIT 1
"""

SQL_ACCOUNT_MODULES_LIST = """
SELECT am.id,
       am.account_id,
       a.name AS account_name,
       am.module_id,
       m.code AS module_code,
       m.name AS module_name,
       am.active
  FROM account_modules am
  JOIN accounts a ON a.id = am.account_id
  JOIN modules m ON m.id = am.module_id
 ORDER BY am.id DESC
"""

SQL_ACCOUNT_MODULES_LIST_PAGED = """
SELECT am.id,
       am.account_id,
       a.name AS account_name,
       am.module_id,
       m.code AS module_code,
       m.name AS module_name,
       am.active
  FROM account_modules am
  JOIN accounts a ON a.id = am.account_id
  JOIN modules m ON m.id = am.module_id
 WHERE (%s = '' OR a.name ILIKE %s OR m.code ILIKE %s OR m.name ILIKE %s OR a.name ILIKE %s)
 ORDER BY
   CASE WHEN %s = 'account_name' AND %s = 'asc' THEN a.name END ASC,
   CASE WHEN %s = 'account_name' AND %s = 'desc' THEN a.name END DESC,
   CASE WHEN %s = 'module_code' AND %s = 'asc' THEN m.code END ASC,
   CASE WHEN %s = 'module_code' AND %s = 'desc' THEN m.code END DESC,
   am.id DESC
 LIMIT %s OFFSET %s
"""

SQL_ACCOUNT_MODULES_COUNT = """
SELECT COUNT(*) AS total
  FROM account_modules am
  JOIN accounts a ON a.id = am.account_id
  JOIN modules m ON m.id = am.module_id
 WHERE (%s = '' OR a.name ILIKE %s OR m.code ILIKE %s OR m.name ILIKE %s OR a.name ILIKE %s)
"""

SQL_ACCOUNT_MODULE_INSERT = """
INSERT INTO account_modules (
    account_id,
    module_id,
    active
) VALUES (%s, %s, %s)
RETURNING id
"""

SQL_ACCOUNT_MODULE_BY_ID = """
SELECT id,
       account_id,
       module_id,
       active,
       created_at
  FROM account_modules
 WHERE id = %s
 LIMIT 1
"""

SQL_ACCOUNT_MODULE_UPDATE = """
UPDATE account_modules
   SET account_id = %s,
       module_id = %s,
       active = %s
 WHERE id = %s
RETURNING id
"""

SQL_ACCOUNT_MODULE_DELETE = """
DELETE FROM account_modules
 WHERE id = %s
RETURNING id
"""

SQL_ACCOUNT_MODULE_BY_ACCOUNT_AND_MODULE = """
SELECT id,
       account_id,
       module_id,
       active,
       created_at
  FROM account_modules
 WHERE account_id = %s
   AND module_id = %s
 LIMIT 1
"""

SQL_TENANT_COMPANIES_LIST = """
SELECT id,
       code,
       document,
       corporate_name,
       fantasy_name,
       phone,
       email,
       city,
       state,
       active,
       created_at,
       updated_at
  FROM companies
 ORDER BY id DESC
"""

SQL_TENANT_COMPANY_INSERT = """
INSERT INTO companies (
    code,
    document,
    corporate_name,
    fantasy_name,
    state_registration,
    municipal_registration,
    phone,
    email,
    zipcode,
    address,
    number,
    district,
    city,
    state,
    logo,
    active
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_TENANT_COMPANY_BY_DOCUMENT = """
SELECT id,
       code,
       document,
       corporate_name
  FROM companies
 WHERE document = %s
 LIMIT 1
"""

SQL_TENANT_USERS_LIST = """
SELECT id,
       company_id,
       name,
       email,
       role_id,
       active,
       created_at
  FROM users
 ORDER BY id DESC
"""

SQL_TENANT_USER_INSERT = """
INSERT INTO users (
    company_id,
    name,
    email,
    password_hash,
    role_id,
    active
) VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_TENANT_USER_BY_EMAIL = """
SELECT id,
       company_id,
       name,
       email,
       role_id
  FROM users
 WHERE email = %s
 LIMIT 1
"""

SQL_TENANT_USER_BY_ID = """
SELECT id,
       company_id,
       name,
       email,
       role_id,
       active
  FROM users
 WHERE id = %s
 LIMIT 1
"""

SQL_TENANT_ROLES_LIST = """
SELECT id,
       name,
       description,
       active,
       created_at
  FROM roles
 ORDER BY id DESC
"""

SQL_TENANT_ROLE_INSERT = """
INSERT INTO roles (
    name,
    description,
    active
) VALUES (%s, %s, %s)
RETURNING id
"""

SQL_TENANT_ROLE_BY_NAME = """
SELECT id,
       name
  FROM roles
 WHERE name = %s
 LIMIT 1
"""

SQL_TENANT_PERMISSIONS_LIST = """
SELECT id,
       code,
       name,
       description,
       active,
       created_at
  FROM permissions
 ORDER BY id DESC
"""

SQL_TENANT_PERMISSION_INSERT = """
INSERT INTO permissions (
    code,
    name,
    description,
    active
) VALUES (%s, %s, %s, %s)
RETURNING id
"""

SQL_TENANT_PERMISSION_BY_CODE = """
SELECT id,
       code,
       name
  FROM permissions
 WHERE code = %s
 LIMIT 1
"""

SQL_TENANT_ROLE_PERMISSIONS_LIST = """
SELECT rp.id,
       rp.role_id,
       r.name AS role_name,
       rp.permission_id,
       p.code AS permission_code,
       p.name AS permission_name,
       rp.created_at
  FROM role_permissions rp
  JOIN roles r ON r.id = rp.role_id
  JOIN permissions p ON p.id = rp.permission_id
 ORDER BY rp.id DESC
"""

SQL_TENANT_ROLE_PERMISSION_INSERT = """
INSERT INTO role_permissions (
    role_id,
    permission_id
) VALUES (%s, %s)
RETURNING id
"""

SQL_TENANT_ROLE_PERMISSION_EXISTS = """
SELECT id
  FROM role_permissions
 WHERE role_id = %s
   AND permission_id = %s
 LIMIT 1
"""

SQL_TENANT_LOGIN = """
SELECT id,
       company_id,
       name,
       email,
       password_hash,
       role,
       role_id,
       active
  FROM users
 WHERE email = %s
 LIMIT 1
"""

SQL_TENANT_ROLE_PERMISSIONS_BY_USER = """
SELECT p.code
  FROM users u
  LEFT JOIN role_permissions rp ON rp.role_id = u.role_id
  LEFT JOIN permissions p ON p.id = rp.permission_id
 WHERE u.id = %s
"""

SQL_PROJECTS_LIST = """
SELECT id,
       name,
       code,
       client_name,
       company_id,
       engineer_user_id,
       address,
       number,
       district,
       city,
       state,
       zipcode,
       latitude,
       longitude,
       budget_amount,
       start_date,
       end_date,
       status,
       created_at,
       updated_at
  FROM projects
 ORDER BY id DESC
"""

SQL_PROJECT_INSERT = """
INSERT INTO projects (
    name,
    code,
    client_name,
    company_id,
    engineer_user_id,
    address,
    number,
    district,
    city,
    state,
    zipcode,
    latitude,
    longitude,
    budget_amount,
    start_date,
    end_date,
    status
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_PROJECT_UPDATE = """
UPDATE projects
   SET name = %s,
       code = %s,
       client_name = %s,
       company_id = %s,
       engineer_user_id = %s,
       address = %s,
       number = %s,
       district = %s,
       city = %s,
       state = %s,
       zipcode = %s,
       latitude = %s,
       longitude = %s,
       budget_amount = %s,
       start_date = %s,
       end_date = %s,
       status = %s,
       updated_at = NOW()
 WHERE id = %s
RETURNING id
"""

SQL_PROJECT_DELETE = """
DELETE FROM projects
 WHERE id = %s
RETURNING id
"""

SQL_TEAMS_LIST = """
SELECT id,
       project_id,
       name,
       description,
       active,
       created_at,
       updated_at
  FROM teams
 ORDER BY id DESC
"""

SQL_TEAM_INSERT = """
INSERT INTO teams (
    project_id,
    name,
    description,
    active
) VALUES (%s, %s, %s, %s)
RETURNING id
"""

SQL_TEAM_UPDATE = """
UPDATE teams
   SET project_id = %s,
       name = %s,
       description = %s,
       active = %s,
       updated_at = NOW()
 WHERE id = %s
RETURNING id
"""

SQL_TEAM_DELETE = """
DELETE FROM teams
 WHERE id = %s
RETURNING id
"""

SQL_TEAM_BY_ID = """
SELECT id,
       project_id,
       name,
       description,
       active
  FROM teams
 WHERE id = %s
 LIMIT 1
"""

SQL_TEAM_MEMBERS_LIST = """
SELECT id,
       team_id,
       user_id,
       member_name,
       role_name,
       active,
       created_at
  FROM team_members
 ORDER BY id DESC
"""

SQL_TEAM_MEMBER_INSERT = """
INSERT INTO team_members (
    team_id,
    user_id,
    member_name,
    role_name,
    active
) VALUES (%s, %s, %s, %s, %s)
RETURNING id
"""

SQL_TEAM_MEMBER_UPDATE = """
UPDATE team_members
   SET team_id = %s,
       user_id = %s,
       member_name = %s,
       role_name = %s,
       active = %s
 WHERE id = %s
RETURNING id
"""

SQL_TEAM_MEMBER_DELETE = """
DELETE FROM team_members
 WHERE id = %s
RETURNING id
"""

SQL_TEAM_MEMBER_BY_ID = """
SELECT id,
       team_id,
       user_id,
       member_name,
       role_name,
       active
  FROM team_members
 WHERE id = %s
 LIMIT 1
"""

SQL_DAILY_OCCURRENCES_LIST = """
SELECT id,
       daily_log_id,
       occurrence_type,
       title,
       description,
       severity,
       resolved,
       created_at
  FROM daily_log_occurrences
 WHERE (%s IS NULL OR daily_log_id = %s)
 ORDER BY id DESC
"""

SQL_DAILY_OCCURRENCE_INSERT = """
INSERT INTO daily_log_occurrences (
    daily_log_id,
    occurrence_type,
    title,
    description,
    severity,
    resolved
) VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DAILY_OCCURRENCE_UPDATE = """
UPDATE daily_log_occurrences
   SET occurrence_type = %s,
       title = %s,
       description = %s,
       severity = %s,
       resolved = %s
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_OCCURRENCE_DELETE = """
DELETE FROM daily_log_occurrences
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_ACTIVITIES_LIST = """
SELECT id,
       daily_log_id,
       service_name,
       quantity,
       unit,
       location,
       notes,
       created_at
  FROM daily_log_activities
 WHERE (%s IS NULL OR daily_log_id = %s)
 ORDER BY id DESC
"""

SQL_DAILY_ACTIVITY_INSERT = """
INSERT INTO daily_log_activities (
    daily_log_id,
    service_name,
    quantity,
    unit,
    location,
    notes
) VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DAILY_ACTIVITY_UPDATE = """
UPDATE daily_log_activities
   SET service_name = %s,
       quantity = %s,
       unit = %s,
       location = %s,
       notes = %s
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_ACTIVITY_DELETE = """
DELETE FROM daily_log_activities
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_LABOR_LIST = """
SELECT id,
       daily_log_id,
       team_member_id,
       worker_name,
       role_name,
       hours_worked,
       present,
       created_at
  FROM daily_log_labor
 WHERE (%s IS NULL OR daily_log_id = %s)
 ORDER BY id DESC
"""

SQL_DAILY_LABOR_INSERT = """
INSERT INTO daily_log_labor (
    daily_log_id,
    team_member_id,
    worker_name,
    role_name,
    hours_worked,
    present
) VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DAILY_LABOR_UPDATE = """
UPDATE daily_log_labor
   SET team_member_id = %s,
       worker_name = %s,
       role_name = %s,
       hours_worked = %s,
       present = %s
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_LABOR_DELETE = """
DELETE FROM daily_log_labor
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_MATERIALS_LIST = """
SELECT id,
       daily_log_id,
       material_name,
       movement_type,
       quantity,
       unit,
       notes,
       created_at
  FROM daily_log_materials
 WHERE (%s IS NULL OR daily_log_id = %s)
 ORDER BY id DESC
"""

SQL_DAILY_MATERIAL_INSERT = """
INSERT INTO daily_log_materials (
    daily_log_id,
    material_name,
    movement_type,
    quantity,
    unit,
    notes
) VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DAILY_MATERIAL_UPDATE = """
UPDATE daily_log_materials
   SET material_name = %s,
       movement_type = %s,
       quantity = %s,
       unit = %s,
       notes = %s
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_MATERIAL_DELETE = """
DELETE FROM daily_log_materials
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_EQUIPMENTS_LIST = """
SELECT id,
       daily_log_id,
       equipment_name,
       status,
       hours_used,
       notes,
       created_at
  FROM daily_log_equipments
 WHERE (%s IS NULL OR daily_log_id = %s)
 ORDER BY id DESC
"""

SQL_DAILY_EQUIPMENT_INSERT = """
INSERT INTO daily_log_equipments (
    daily_log_id,
    equipment_name,
    status,
    hours_used,
    notes
) VALUES (%s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DAILY_EQUIPMENT_UPDATE = """
UPDATE daily_log_equipments
   SET equipment_name = %s,
       status = %s,
       hours_used = %s,
       notes = %s
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_EQUIPMENT_DELETE = """
DELETE FROM daily_log_equipments
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_FILES_LIST = """
SELECT id,
       daily_log_id,
       file_name,
       file_type,
       file_url,
       file_size_bytes,
       notes,
       created_at
  FROM daily_log_files
 WHERE (%s IS NULL OR daily_log_id = %s)
 ORDER BY id DESC
"""

SQL_DAILY_FILE_INSERT = """
INSERT INTO daily_log_files (
    daily_log_id,
    file_name,
    file_type,
    file_url,
    file_size_bytes,
    notes
) VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DAILY_FILE_UPDATE = """
UPDATE daily_log_files
   SET file_name = %s,
       file_type = %s,
       file_url = %s,
       file_size_bytes = %s,
       notes = %s
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_FILE_DELETE = """
DELETE FROM daily_log_files
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_SIGNATURES_LIST = """
SELECT id,
       daily_log_id,
       signed_by_user_id,
       signer_name,
       signature_type,
       signature_data,
       signed_at
  FROM daily_log_signatures
 WHERE (%s IS NULL OR daily_log_id = %s)
 ORDER BY id DESC
"""

SQL_DAILY_SIGNATURE_INSERT = """
INSERT INTO daily_log_signatures (
    daily_log_id,
    signed_by_user_id,
    signer_name,
    signature_type,
    signature_data
) VALUES (%s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DAILY_SIGNATURE_UPDATE = """
UPDATE daily_log_signatures
   SET signed_by_user_id = %s,
       signer_name = %s,
       signature_type = %s,
       signature_data = %s
 WHERE id = %s
RETURNING id
"""

SQL_DAILY_SIGNATURE_DELETE = """
DELETE FROM daily_log_signatures
 WHERE id = %s
RETURNING id
"""

SQL_DIARY_FILTERED_LIST = """
SELECT id,
       project_id,
       work_date,
       weather,
       summary,
       created_by,
       status,
       created_at,
       updated_at
  FROM daily_logs
 WHERE (%s IS NULL OR project_id = %s)
   AND (%s = '' OR status = %s)
   AND (%s IS NULL OR created_by = %s)
   AND (%s IS NULL OR work_date >= %s)
   AND (%s IS NULL OR work_date <= %s)
 ORDER BY work_date DESC, id DESC
"""

SQL_PRODUCTION_FILTERED_LIST = """
SELECT id,
       project_id,
       reference_date,
       service_name,
       unit,
       planned_quantity,
       executed_quantity,
       notes,
       created_by,
       created_at,
       updated_at
  FROM production_entries
 WHERE (%s IS NULL OR project_id = %s)
   AND (%s IS NULL OR created_by = %s)
   AND (%s IS NULL OR reference_date >= %s)
   AND (%s IS NULL OR reference_date <= %s)
 ORDER BY reference_date DESC, id DESC
"""

SQL_AUDIT_LOGS_LIST = """
SELECT id,
       account_id,
       user_id,
       module,
       action,
       table_name,
       record_id,
       ip_address,
       payload,
       created_at
  FROM audit_logs
 WHERE (%s = '' OR module = %s)
   AND (%s = '' OR action = %s)
   AND (%s = '' OR table_name = %s)
   AND (%s IS NULL OR record_id = %s)
   AND (%s IS NULL OR created_at::date >= %s)
   AND (%s IS NULL OR created_at::date <= %s)
 ORDER BY created_at DESC, id DESC
 LIMIT 500
"""

SQL_AUDIT_LOGS_LIST_LIMITED = """
SELECT id,
       account_id,
       user_id,
       COALESCE(mu.name, tu.name) AS user_name,
       module,
       action,
       table_name,
       record_id,
       ip_address,
       payload,
       created_at
  FROM audit_logs al
  LEFT JOIN master_users mu ON mu.id = al.user_id
  LEFT JOIN users tu ON tu.id = al.user_id
 WHERE (%s = '' OR module = %s)
   AND (%s = '' OR action = %s)
   AND (%s = '' OR table_name = %s)
   AND (%s IS NULL OR record_id = %s)
   AND (%s IS NULL OR created_at::date >= %s)
   AND (%s IS NULL OR created_at::date <= %s)
 ORDER BY created_at DESC, id DESC
 LIMIT %s
OFFSET %s
"""

SQL_AUDIT_SUMMARY = """
SELECT module,
       action,
       table_name,
       COUNT(*) AS total
  FROM audit_logs
 WHERE (%s = '' OR module = %s)
   AND (%s IS NULL OR created_at::date >= %s)
   AND (%s IS NULL OR created_at::date <= %s)
 GROUP BY module, action, table_name
 ORDER BY module, action, table_name
"""

SQL_AUDIT_TIMELINE_PROJECT = """
SELECT id,
       account_id,
       user_id,
       COALESCE(mu.name, tu.name) AS user_name,
       module,
       action,
       table_name,
       record_id,
       ip_address,
       payload,
       created_at
  FROM audit_logs al
  LEFT JOIN master_users mu ON mu.id = al.user_id
  LEFT JOIN users tu ON tu.id = al.user_id
 WHERE (
        (table_name = 'projects' AND record_id = %s)
        OR payload LIKE %s
       )
 ORDER BY created_at DESC, id DESC
 LIMIT %s
"""

SQL_AUDIT_TIMELINE_DIARY = """
SELECT id,
       account_id,
       user_id,
       COALESCE(mu.name, tu.name) AS user_name,
       module,
       action,
       table_name,
       record_id,
       ip_address,
       payload,
       created_at
  FROM audit_logs al
  LEFT JOIN master_users mu ON mu.id = al.user_id
  LEFT JOIN users tu ON tu.id = al.user_id
 WHERE (
        (table_name = 'daily_logs' AND record_id = %s)
        OR payload LIKE %s
       )
 ORDER BY created_at DESC, id DESC
 LIMIT %s
"""

SQL_INDICATORS_DIARY_BY_USER = """
SELECT u.id AS user_id,
       u.name AS user_name,
       COUNT(dl.id) AS diaries_count,
       COUNT(CASE WHEN dl.status = 'approved' THEN 1 END) AS approved_diaries,
       COUNT(CASE WHEN dl.status IN ('draft', 'rejected') THEN 1 END) AS pending_diaries
  FROM users u
  LEFT JOIN daily_logs dl ON dl.created_by = u.id
 WHERE (%s IS NULL OR dl.project_id = %s)
   AND (%s IS NULL OR dl.work_date >= %s)
   AND (%s IS NULL OR dl.work_date <= %s)
 GROUP BY u.id, u.name
 HAVING COUNT(dl.id) > 0
 ORDER BY diaries_count DESC, u.name
"""

SQL_INDICATORS_PRODUCTION_BY_USER = """
SELECT u.id AS user_id,
       u.name AS user_name,
       COUNT(pe.id) AS production_entries_count,
       COALESCE(SUM(pe.planned_quantity), 0) AS planned_quantity_total,
       COALESCE(SUM(pe.executed_quantity), 0) AS executed_quantity_total
  FROM users u
  LEFT JOIN production_entries pe ON pe.created_by = u.id
 WHERE (%s IS NULL OR pe.project_id = %s)
   AND (%s IS NULL OR pe.reference_date >= %s)
   AND (%s IS NULL OR pe.reference_date <= %s)
 GROUP BY u.id, u.name
 HAVING COUNT(pe.id) > 0
 ORDER BY executed_quantity_total DESC, u.name
"""

SQL_DASHBOARD_USER_SUMMARY = """
SELECT
    u.id AS user_id,
    u.name AS user_name,
    COALESCE(d.diaries_count, 0) AS diaries_count,
    COALESCE(d.approved_diaries, 0) AS approved_diaries,
    COALESCE(d.pending_diaries, 0) AS pending_diaries,
    COALESCE(p.production_entries_count, 0) AS production_entries_count,
    COALESCE(p.planned_quantity_total, 0) AS planned_quantity_total,
    COALESCE(p.executed_quantity_total, 0) AS executed_quantity_total
FROM users u
LEFT JOIN (
    SELECT created_by,
           COUNT(id) AS diaries_count,
           COUNT(CASE WHEN status = 'approved' THEN 1 END) AS approved_diaries,
           COUNT(CASE WHEN status IN ('draft', 'rejected') THEN 1 END) AS pending_diaries
      FROM daily_logs
     WHERE (%s IS NULL OR project_id = %s)
       AND (%s IS NULL OR work_date >= %s)
       AND (%s IS NULL OR work_date <= %s)
     GROUP BY created_by
) d ON d.created_by = u.id
LEFT JOIN (
    SELECT created_by,
           COUNT(id) AS production_entries_count,
           COALESCE(SUM(planned_quantity), 0) AS planned_quantity_total,
           COALESCE(SUM(executed_quantity), 0) AS executed_quantity_total
      FROM production_entries
     WHERE (%s IS NULL OR project_id = %s)
       AND (%s IS NULL OR reference_date >= %s)
       AND (%s IS NULL OR reference_date <= %s)
     GROUP BY created_by
) p ON p.created_by = u.id
WHERE COALESCE(d.diaries_count, 0) > 0
   OR COALESCE(p.production_entries_count, 0) > 0
ORDER BY executed_quantity_total DESC, diaries_count DESC, u.name
"""

SQL_DASHBOARD_SUMMARY = """
SELECT
    (SELECT COUNT(*) FROM projects WHERE status = 'active') AS active_projects,
    (SELECT COUNT(*) FROM daily_logs WHERE status IN ('draft', 'rejected')) AS pending_diaries,
    (SELECT COUNT(*) FROM daily_log_occurrences WHERE resolved = FALSE) AS open_occurrences,
    (SELECT COALESCE(SUM(executed_quantity), 0) FROM production_entries) AS total_executed_quantity
"""

SQL_DASHBOARD_LAST_DIARIES = """
SELECT id,
       project_id,
       work_date,
       weather,
       summary,
       status,
       created_at
  FROM daily_logs
 ORDER BY work_date DESC, id DESC
 LIMIT 10
"""

SQL_DASHBOARD_PROJECT_PRODUCTIVITY = """
SELECT p.id AS project_id,
       p.name AS project_name,
       COALESCE(SUM(pe.executed_quantity), 0) AS executed_quantity,
       COUNT(DISTINCT dl.id) AS diaries_count
  FROM projects p
  LEFT JOIN production_entries pe ON pe.project_id = p.id
  LEFT JOIN daily_logs dl ON dl.project_id = p.id
 GROUP BY p.id, p.name
 ORDER BY p.name
"""

SQL_REPORT_PROJECT_DIARIES = """
SELECT dl.id,
       dl.project_id,
       p.name AS project_name,
       dl.work_date,
       dl.weather,
       dl.summary,
       dl.status,
       COALESCE(COUNT(DISTINCT da.id), 0) AS activities_count,
       COALESCE(COUNT(DISTINCT doc.id), 0) AS occurrences_count,
       COALESCE(COUNT(DISTINCT dm.id), 0) AS materials_count,
       COALESCE(COUNT(DISTINCT de.id), 0) AS equipments_count
  FROM daily_logs dl
  JOIN projects p ON p.id = dl.project_id
  LEFT JOIN daily_log_activities da ON da.daily_log_id = dl.id
  LEFT JOIN daily_log_occurrences doc ON doc.daily_log_id = dl.id
  LEFT JOIN daily_log_materials dm ON dm.daily_log_id = dl.id
  LEFT JOIN daily_log_equipments de ON de.daily_log_id = dl.id
 WHERE (%s IS NULL OR dl.project_id = %s)
   AND (%s IS NULL OR dl.work_date >= %s)
   AND (%s IS NULL OR dl.work_date <= %s)
 GROUP BY dl.id, dl.project_id, p.name, dl.work_date, dl.weather, dl.summary, dl.status
 ORDER BY dl.work_date DESC, dl.id DESC
"""

SQL_REPORT_PROJECT_SUMMARY = """
SELECT p.id AS project_id,
       p.name AS project_name,
       COUNT(DISTINCT dl.id) AS diaries_count,
       COUNT(DISTINCT CASE WHEN dl.status = 'approved' THEN dl.id END) AS approved_diaries,
       COUNT(DISTINCT CASE WHEN dl.status IN ('draft', 'rejected') THEN dl.id END) AS pending_diaries,
       COUNT(DISTINCT doc.id) AS occurrences_count,
       COUNT(DISTINCT CASE WHEN doc.resolved = FALSE THEN doc.id END) AS open_occurrences,
       COALESCE(SUM(DISTINCT pe.executed_quantity), 0) AS total_executed_quantity
  FROM projects p
  LEFT JOIN daily_logs dl ON dl.project_id = p.id
  LEFT JOIN daily_log_occurrences doc ON doc.daily_log_id = dl.id
  LEFT JOIN production_entries pe ON pe.project_id = p.id
 WHERE (%s IS NULL OR p.id = %s)
   AND (%s IS NULL OR dl.work_date >= %s)
   AND (%s IS NULL OR dl.work_date <= %s)
 GROUP BY p.id, p.name
 ORDER BY p.name
"""

SQL_PROJECT_BY_ID = """
SELECT id,
       name,
       code,
       client_name,
       company_id,
       engineer_user_id,
       address,
       number,
       district,
       city,
       state,
       zipcode,
       latitude,
       longitude,
       budget_amount,
       start_date,
       end_date,
       status,
       created_at,
       updated_at
  FROM projects
 WHERE id = %s
 LIMIT 1
"""

SQL_AUDIT_LOG_INSERT = """
INSERT INTO audit_logs (
    account_id,
    user_id,
    module,
    action,
    table_name,
    record_id,
    ip_address,
    payload
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id
"""

SQL_DAILY_OCCURRENCE_BY_ID = """
SELECT id,
       daily_log_id
  FROM daily_log_occurrences
 WHERE id = %s
 LIMIT 1
"""

SQL_DAILY_ACTIVITY_BY_ID = """
SELECT id,
       daily_log_id
  FROM daily_log_activities
 WHERE id = %s
 LIMIT 1
"""

SQL_DAILY_LABOR_BY_ID = """
SELECT id,
       daily_log_id
  FROM daily_log_labor
 WHERE id = %s
 LIMIT 1
"""

SQL_DAILY_MATERIAL_BY_ID = """
SELECT id,
       daily_log_id
  FROM daily_log_materials
 WHERE id = %s
 LIMIT 1
"""

SQL_DAILY_EQUIPMENT_BY_ID = """
SELECT id,
       daily_log_id
  FROM daily_log_equipments
 WHERE id = %s
 LIMIT 1
"""

SQL_DAILY_FILE_BY_ID = """
SELECT id,
       daily_log_id
  FROM daily_log_files
 WHERE id = %s
 LIMIT 1
"""

SQL_DAILY_SIGNATURE_BY_ID = """
SELECT id,
       daily_log_id
  FROM daily_log_signatures
 WHERE id = %s
 LIMIT 1
"""

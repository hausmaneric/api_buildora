CREATE TABLE IF NOT EXISTS database_metadata (
    id BIGSERIAL PRIMARY KEY,
    metadata_key VARCHAR(100) NOT NULL UNIQUE,
    metadata_value TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS plans (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(300),
    price NUMERIC(18, 2) NOT NULL DEFAULT 0,
    max_companies INT NOT NULL DEFAULT 0,
    max_users INT NOT NULL DEFAULT 0,
    max_works INT NOT NULL DEFAULT 0,
    max_storage_mb BIGINT NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS modules (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(300),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    document VARCHAR(20),
    phone VARCHAR(30),
    email VARCHAR(150),
    status INT NOT NULL DEFAULT 1,
    plan_id BIGINT REFERENCES plans(id),
    database_url TEXT,
    database_host VARCHAR(200),
    database_port INT,
    database_name VARCHAR(150),
    database_user VARCHAR(150),
    database_password VARCHAR(300),
    database_sslmode VARCHAR(20),
    storage_limit_mb BIGINT NOT NULL DEFAULT 0,
    storage_used_mb BIGINT NOT NULL DEFAULT 0,
    expiration_date TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS account_modules (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(id),
    module_id BIGINT NOT NULL REFERENCES modules(id),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS master_users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(500) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(30),
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(id),
    plan_id BIGINT NOT NULL REFERENCES plans(id),
    start_date TIMESTAMP NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP,
    amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    status INT NOT NULL DEFAULT 1,
    payment_method VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    id BIGSERIAL PRIMARY KEY,
    subscription_id BIGINT NOT NULL REFERENCES subscriptions(id),
    payment_date TIMESTAMP,
    amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    transaction_id VARCHAR(200),
    status INT NOT NULL DEFAULT 0,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES accounts(id),
    user_id BIGINT,
    module VARCHAR(100),
    action VARCHAR(100),
    table_name VARCHAR(100),
    record_id BIGINT,
    ip_address VARCHAR(100),
    payload TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS support_access (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(id),
    user_id BIGINT REFERENCES master_users(id),
    access_start TIMESTAMP,
    access_end TIMESTAMP,
    reason VARCHAR(300),
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(id),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type INT NOT NULL DEFAULT 0,
    viewed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(300),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS permissions (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    description VARCHAR(300),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS role_permissions (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES roles(id),
    permission_id BIGINT NOT NULL REFERENCES permissions(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS companies (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(20),
    document VARCHAR(20),
    corporate_name VARCHAR(200) NOT NULL,
    fantasy_name VARCHAR(200),
    state_registration VARCHAR(50),
    municipal_registration VARCHAR(50),
    phone VARCHAR(30),
    email VARCHAR(150),
    zipcode VARCHAR(15),
    address VARCHAR(200),
    number VARCHAR(20),
    district VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(2),
    logo TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id),
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    role_id BIGINT REFERENCES roles(id),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50),
    client_name VARCHAR(150),
    company_id BIGINT REFERENCES companies(id),
    engineer_user_id BIGINT REFERENCES users(id),
    address VARCHAR(200),
    number VARCHAR(20),
    district VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(2),
    zipcode VARCHAR(15),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    budget_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    start_date DATE,
    end_date DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teams (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL REFERENCES projects(id),
    name VARCHAR(150) NOT NULL,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS team_members (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL REFERENCES teams(id),
    user_id BIGINT REFERENCES users(id),
    member_name VARCHAR(150) NOT NULL,
    role_name VARCHAR(100),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_logs (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL REFERENCES projects(id),
    work_date DATE NOT NULL,
    weather VARCHAR(50),
    summary TEXT,
    occurrences TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_log_occurrences (
    id BIGSERIAL PRIMARY KEY,
    daily_log_id BIGINT NOT NULL REFERENCES daily_logs(id),
    occurrence_type VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    severity VARCHAR(30),
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_log_activities (
    id BIGSERIAL PRIMARY KEY,
    daily_log_id BIGINT NOT NULL REFERENCES daily_logs(id),
    service_name VARCHAR(150) NOT NULL,
    quantity NUMERIC(18, 4) NOT NULL DEFAULT 0,
    unit VARCHAR(20),
    location VARCHAR(150),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_log_labor (
    id BIGSERIAL PRIMARY KEY,
    daily_log_id BIGINT NOT NULL REFERENCES daily_logs(id),
    team_member_id BIGINT REFERENCES team_members(id),
    worker_name VARCHAR(150) NOT NULL,
    role_name VARCHAR(100),
    hours_worked NUMERIC(10, 2) NOT NULL DEFAULT 0,
    present BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_log_materials (
    id BIGSERIAL PRIMARY KEY,
    daily_log_id BIGINT NOT NULL REFERENCES daily_logs(id),
    material_name VARCHAR(150) NOT NULL,
    movement_type VARCHAR(30) NOT NULL,
    quantity NUMERIC(18, 4) NOT NULL DEFAULT 0,
    unit VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_log_equipments (
    id BIGSERIAL PRIMARY KEY,
    daily_log_id BIGINT NOT NULL REFERENCES daily_logs(id),
    equipment_name VARCHAR(150) NOT NULL,
    status VARCHAR(30) NOT NULL,
    hours_used NUMERIC(10, 2) NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_log_files (
    id BIGSERIAL PRIMARY KEY,
    daily_log_id BIGINT NOT NULL REFERENCES daily_logs(id),
    file_name VARCHAR(200) NOT NULL,
    file_type VARCHAR(30) NOT NULL,
    file_url TEXT,
    file_size_bytes BIGINT NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_log_signatures (
    id BIGSERIAL PRIMARY KEY,
    daily_log_id BIGINT NOT NULL REFERENCES daily_logs(id),
    signed_by_user_id BIGINT REFERENCES users(id),
    signer_name VARCHAR(150) NOT NULL,
    signature_type VARCHAR(30) NOT NULL,
    signature_data TEXT,
    signed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS production_entries (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL REFERENCES projects(id),
    reference_date DATE NOT NULL,
    service_name VARCHAR(150) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    planned_quantity NUMERIC(18, 4) NOT NULL DEFAULT 0,
    executed_quantity NUMERIC(18, 4) NOT NULL DEFAULT 0,
    notes TEXT,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

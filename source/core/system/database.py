from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from source.core.config.config import appConfig  # noqa: E402
from source.core.system.express import FDExpress  # noqa: E402
from source.core.system.utils import NXResult  # noqa: E402


def build_connection_string() -> str:
    if appConfig.databaseUrl:
        return appConfig.databaseUrl

    return (
        f"host={appConfig.dbHost} "
        f"port={appConfig.dbPort} "
        f"dbname={appConfig.dbName} "
        f"user={appConfig.dbUser} "
        f"password={appConfig.dbPassword} "
        f"sslmode={appConfig.dbSslMode}"
    )


def build_tenant_connection_string(account: dict[str, Any]) -> str:
    if account.get('database_url'):
        return account['database_url']

    return (
        f"host={account.get('database_host', appConfig.dbHost)} "
        f"port={account.get('database_port', appConfig.dbPort)} "
        f"dbname={account.get('database_name')} "
        f"user={account.get('database_user')} "
        f"password={account.get('database_password')} "
        f"sslmode={account.get('database_sslmode', appConfig.dbSslMode)}"
    )


def validate_master_database_config() -> dict:
    issues = []
    mode = 'database_url' if appConfig.databaseUrl else 'discrete'

    if appConfig.databaseUrl:
        if '://' not in appConfig.databaseUrl and 'host=' not in appConfig.databaseUrl:
            issues.append('OBRAX_DATABASE_URL parece invalida')
    else:
        required_map = {
            'OBRAX_DB_HOST': appConfig.dbHost,
            'OBRAX_DB_PORT': appConfig.dbPort,
            'OBRAX_DB_NAME': appConfig.dbName,
            'OBRAX_DB_USER': appConfig.dbUser,
            'OBRAX_DB_PASSWORD': appConfig.dbPassword,
        }
        for key, value in required_map.items():
            if value in [None, '', 0]:
                issues.append(f'{key} nao configurado')

    return {
        'valid': len(issues) == 0,
        'mode': mode,
        'issues': issues,
    }


class NXDatabaseConnection:
    def __init__(self) -> None:
        self.result = NXResult()
        self.conn_nx = None
        self.xp_nx = None
        self.activate = False

    def stop(self):
        if self.activate and self.conn_nx:
            self.conn_nx.close()
        self.activate = False
        self.conn_nx = None
        self.xp_nx = None

    def _open(self, connection_string: str, error_message: str) -> NXResult:
        result = NXResult()
        try:
            self.conn_nx = psycopg2.connect(connection_string, cursor_factory=RealDictCursor)
            self.xp_nx = FDExpress(self.conn_nx)
            self.activate = True
            result.status = True
        except Exception as e:
            result.make_error(0, error_message, str(e))
            self.activate = False
        return result


class NXMasterConnection(NXDatabaseConnection):
    def active(self) -> NXResult:
        return self._open(build_connection_string(), 'Falha na conexao com a base de dados')


class NXTenantConnection(NXDatabaseConnection):
    def active_by_account(self, account: dict[str, Any]) -> NXResult:
        return self._open(build_tenant_connection_string(account), 'Falha na conexao com a base do ambiente')


__all__ = [
    'NXMasterConnection',
    'NXTenantConnection',
    'build_connection_string',
    'build_tenant_connection_string',
    'validate_master_database_config',
]


def master_database_ping() -> NXResult:
    result = NXResult()
    validation = validate_master_database_config()
    if validation['valid'] is False:
        result.make_error(0, 'Configuracao do banco principal invalida', '; '.join(validation['issues']))
        result.data = validation
        return result

    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened

    try:
        rs = nx.xp_nx.FDXQuery('SELECT 1 AS ok')
        if rs.error:
            result.make_error(0, 'Falha ao consultar banco principal', rs.message)
        else:
            result.status = True
            result.message = 'Banco principal acessivel'
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {'ok': 1}
    except Exception as e:
        result.make_error(0, 'Falha no ping do banco principal', str(e))
    finally:
        nx.stop()

    return result

from typing import Any

import psycopg2
from psycopg2 import pool
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
    _pool_registry: dict[str, pool.SimpleConnectionPool] = {}

    def __init__(self) -> None:
        self.result = NXResult()
        self.conn_nx = None
        self.xp_nx = None
        self.activate = False
        self._pool_key = None

    def stop(self):
        if self.activate and self.conn_nx:
            try:
                if self._pool_key and self._pool_key in self._pool_registry:
                    close_bad = bool(getattr(self.conn_nx, 'closed', 0))
                    self._pool_registry[self._pool_key].putconn(self.conn_nx, close=close_bad)
                else:
                    self.conn_nx.close()
            except Exception:
                try:
                    self.conn_nx.close()
                except Exception:
                    pass
        self.activate = False
        self.conn_nx = None
        self.xp_nx = None
        self._pool_key = None

    @classmethod
    def _get_pool(cls, connection_string: str) -> pool.SimpleConnectionPool:
        if connection_string not in cls._pool_registry:
            cls._pool_registry[connection_string] = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=connection_string,
                cursor_factory=RealDictCursor,
            )
        return cls._pool_registry[connection_string]

    @classmethod
    def _reset_pool(cls, connection_string: str) -> None:
        existing = cls._pool_registry.pop(connection_string, None)
        if existing:
            try:
                existing.closeall()
            except Exception:
                pass

    def _validate_connection(self, connection: psycopg2.extensions.connection) -> None:
        if getattr(connection, 'closed', 0):
            raise psycopg2.OperationalError('Conexao encerrada pelo servidor')

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute('SELECT 1 AS ok')
            cursor.fetchone()
            connection.rollback()
        finally:
            cursor.close()

    def _open(self, connection_string: str, error_message: str) -> NXResult:
        result = NXResult()
        last_error = None

        for attempt in range(2):
            try:
                conn_pool = self._get_pool(connection_string)
                candidate = conn_pool.getconn()
                try:
                    self._validate_connection(candidate)
                except Exception:
                    try:
                        conn_pool.putconn(candidate, close=True)
                    except Exception:
                        try:
                            candidate.close()
                        except Exception:
                            pass
                    raise

                self.conn_nx = candidate
                self.xp_nx = FDExpress(self.conn_nx)
                self._pool_key = connection_string
                self.activate = True
                result.status = True
                return result
            except Exception as e:
                last_error = e
                self.activate = False
                self.conn_nx = None
                self.xp_nx = None
                self._pool_key = None
                if attempt == 0:
                    self._reset_pool(connection_string)

        result.make_error(0, error_message, str(last_error))
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

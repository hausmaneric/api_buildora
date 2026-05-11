import base64
from datetime import date, datetime, timedelta
import hashlib
import json
import jwt
import os
from typing import Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from classes.express import FDExpress
from classes.next_base import NXResult
from controller import nxc
import psycopg2
from psycopg2.extras import RealDictCursor


def generate_aes_key_iv():
    return os.urandom(32), os.urandom(16)


def encrypt_aes_b64(data: str, key: bytes, iv: bytes) -> str:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    data_padded = data + (16 - len(data) % 16) * chr(16 - len(data) % 16)
    encrypted = encryptor.update(data_padded.encode('utf-8')) + encryptor.finalize()
    return base64.urlsafe_b64encode(encrypted).decode('utf-8')


def decrypt_aes_b64(encrypted_data: str, key: bytes, iv: bytes) -> str:
    padded = encrypted_data + '=' * (-len(encrypted_data) % 4)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    encrypted_bytes = base64.urlsafe_b64decode(padded.encode('utf-8'))
    decrypted_padded = decryptor.update(encrypted_bytes) + decryptor.finalize()
    padding_length = decrypted_padded[-1]
    return decrypted_padded[:-padding_length].decode('utf-8')


def parse_date(value):
    return value.strftime('%d/%m/%Y') if value else None


def format_date(date_str: str | None) -> date | None:
    if date_str:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    return None


def format_date_to_string(date_obj: date | None) -> str | None:
    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    return None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def serialize_payload(payload: Any) -> str:
    try:
        return json.dumps(payload, ensure_ascii=False, default=str)
    except Exception:
        return str(payload)


def generate_token(payload: dict[str, Any]) -> str:
    safe_payload = dict(payload)
    safe_payload['exp'] = datetime.utcnow() + timedelta(days=1)
    return jwt.encode(safe_payload, nxc.OBRAX_SECRET_KEY, algorithm='HS256')


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, nxc.OBRAX_SECRET_KEY, algorithms=['HS256'])


def build_connection_string() -> str:
    if nxc.OBRAX_DATABASE_URL:
        return nxc.OBRAX_DATABASE_URL

    return (
        f"host={nxc.OBRAX_DB_HOST} "
        f"port={nxc.OBRAX_DB_PORT} "
        f"dbname={nxc.OBRAX_DB_NAME} "
        f"user={nxc.OBRAX_DB_USER} "
        f"password={nxc.OBRAX_DB_PASSWORD} "
        f"sslmode={nxc.OBRAX_DB_SSLMODE}"
    )


def build_tenant_connection_string(account: dict[str, Any]) -> str:
    if account.get('database_url'):
        return account['database_url']

    return (
        f"host={account.get('database_host', nxc.OBRAX_DB_HOST)} "
        f"port={account.get('database_port', nxc.OBRAX_DB_PORT)} "
        f"dbname={account.get('database_name')} "
        f"user={account.get('database_user')} "
        f"password={account.get('database_password')} "
        f"sslmode={account.get('database_sslmode', nxc.OBRAX_DB_SSLMODE)}"
    )


class NXConnection(object):
    def __init__(self) -> None:
        self.result = NXResult()
        self.conn_nx = None
        self.xp_nx = None
        self.activate = False

    def stop(self):
        if self.activate and self.conn_nx:
            self.conn_nx.close()
            self.activate = False

    def active(self) -> NXResult:
        result = NXResult()
        try:
            self.conn_nx = psycopg2.connect(build_connection_string(), cursor_factory=RealDictCursor)
            self.xp_nx = FDExpress(self.conn_nx)
            self.activate = True
            result.status = True
        except Exception as e:
            result.make_error(0, 'Falha na conexão com a base de dados', str(e))
            self.activate = False
        return result

    def login_connection(self, token: str) -> NXResult:
        result = NXResult()
        try:
            payload = decode_token(token.replace('Bearer ', ''))
            if not payload.get('user_id'):
                result.make_error(0, 'Token inválido')
                return result
        except Exception as e:
            result.make_error(0, 'Falha na autenticação', str(e))
            return result

        connection = self.active()
        if not connection.error:
            result.status = True
        else:
            result.make_error(0, connection.message)
        return result


class NXMasterConnection(NXConnection):
    pass


class NXTenantConnection(NXConnection):
    def active_by_account(self, account: dict[str, Any]) -> NXResult:
        result = NXResult()
        try:
            self.conn_nx = psycopg2.connect(
                build_tenant_connection_string(account),
                cursor_factory=RealDictCursor,
            )
            self.xp_nx = FDExpress(self.conn_nx)
            self.activate = True
            result.status = True
        except Exception as e:
            result.make_error(0, 'Falha na conexão com a base do ambiente', str(e))
            self.activate = False
        return result


def write_audit_log(
    connection: NXConnection,
    account_id: int | None,
    user_id: int | None,
    module: str,
    action: str,
    table_name: str,
    record_id: int | None,
    ip_address: str | None,
    payload: Any,
):
    from classes.sql.obx_sql import SQL_AUDIT_LOG_INSERT

    return connection.xp_nx.FDXQuery(
        SQL_AUDIT_LOG_INSERT,
        account_id,
        user_id,
        module,
        action,
        table_name,
        record_id,
        ip_address,
        serialize_payload(payload),
    )

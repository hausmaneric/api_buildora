import hashlib
import json
from typing import Any

from source.data.sql.sql_obrax import SQL_AUDIT_LOG_INSERT


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def serialize_payload(payload: Any) -> str:
    try:
        return json.dumps(payload, ensure_ascii=False, default=str)
    except Exception:
        return str(payload)


def write_audit_log(
    connection: Any,
    account_id: int | None,
    user_id: int | None,
    module: str,
    action: str,
    table_name: str,
    record_id: int | None,
    ip_address: str | None,
    payload: Any,
):
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

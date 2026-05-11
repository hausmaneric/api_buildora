from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from source.core.system.auth import authenticate_master, authenticate_tenant, open_tenant_connection  # noqa: E402
from source.core.system.database import NXMasterConnection  # noqa: E402
from source.core.system.utils import NXResult, decode_token  # noqa: E402


class NXLoginType(Enum):
    NONE = 0
    ORB = 1
    SYSTEM = 2


@dataclass
class NXSession:
    userid: int = 0
    token: str = ''
    scope: str = ''
    account_code: str = ''
    permissions: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)


class NXConnection:
    def __init__(self) -> None:
        self.result = NXResult()
        self.conn_nx = None
        self.xp_nx = None
        self.activate = False
        self.session = NXSession()
        self._tenant = None
        self._master = None

    def stop(self):
        if self._tenant:
            self._tenant.stop()
            self._tenant = None
        if self._master:
            self._master.stop()
            self._master = None
        self.activate = False

    def authenticate_master(self, login: str, password: str) -> NXResult:
        return authenticate_master(login, password)

    def authenticate_tenant(self, account_code: str, email: str, password: str) -> NXResult:
        return authenticate_tenant(account_code, email, password)

    def has_permission(self, *permission_codes: str) -> bool:
        if self.session.scope != 'tenant':
            return False

        granted = set(self.session.permissions or [])
        for code in permission_codes:
            if code and code in granted:
                return True
        return False

    def login(self, login_type: NXLoginType, token_id: str) -> NXResult:
        result = NXResult()
        try:
            payload = decode_token(token_id.replace('Bearer ', '').strip())
        except Exception as e:
            result.make_error(0, 'Falha na autenticacao', str(e))
            return result

        self.session.userid = payload.get('user_id', 0)
        self.session.token = token_id
        self.session.scope = payload.get('scope', '')
        self.session.account_code = payload.get('account_code', '')
        self.session.permissions = payload.get('permissions', []) or []
        self.session.payload = payload

        if login_type == NXLoginType.SYSTEM:
            opened, tenant, _account = open_tenant_connection(self.session.account_code)
            if opened.error:
                return opened
            self._tenant = tenant
            self.conn_nx = tenant.conn_nx
            self.xp_nx = tenant.xp_nx
            self.activate = True
            ok = NXResult()
            ok.status = True
            return ok

        self._master = NXMasterConnection()
        opened = self._master.active()
        if opened.error:
            return opened
        self.conn_nx = self._master.conn_nx
        self.xp_nx = self._master.xp_nx
        self.activate = True
        ok = NXResult()
        ok.status = True
        return ok


def require_tenant_permissions(nx: NXConnection, *permission_codes: str) -> NXResult:
    result = NXResult()
    if nx.session.scope != 'tenant':
        result.make_error(403, 'Token sem permissao tenant')
        return result

    if not permission_codes:
        result.status = True
        return result

    if nx.has_permission(*permission_codes):
        result.status = True
        return result

    result.make_error(403, f'Permissao obrigatoria nao concedida: {" ou ".join(permission_codes)}')
    return result


def require_tenant_permissions_all(nx: NXConnection, *permission_codes: str) -> NXResult:
    result = NXResult()
    if nx.session.scope != 'tenant':
        result.make_error(403, 'Token sem permissao tenant')
        return result

    granted = set(nx.session.permissions or [])
    missing = [code for code in permission_codes if code and code not in granted]
    if missing:
        result.make_error(403, f'Permissoes obrigatorias nao concedidas: {", ".join(missing)}')
        return result

    result.status = True
    return result

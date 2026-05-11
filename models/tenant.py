from dataclasses import dataclass
from typing import Any
from models.nxm import DefaulModelClass


@dataclass
class TenantCompanyInput(DefaulModelClass):
    code: str = ''
    document: str = ''
    corporate_name: str = ''
    fantasy_name: str = ''
    state_registration: str = ''
    municipal_registration: str = ''
    phone: str = ''
    email: str = ''
    zipcode: str = ''
    address: str = ''
    number: str = ''
    district: str = ''
    city: str = ''
    state: str = ''
    logo: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'TenantCompanyInput':
        return TenantCompanyInput(**{key: obj.get(key, getattr(TenantCompanyInput(), key)) for key in TenantCompanyInput.__annotations__})


@dataclass
class TenantUserInput(DefaulModelClass):
    company_id: int = 0
    name: str = ''
    email: str = ''
    password: str = ''
    role_id: int | None = None
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'TenantUserInput':
        return TenantUserInput(**{key: obj.get(key, getattr(TenantUserInput(), key)) for key in TenantUserInput.__annotations__})


@dataclass
class TenantRoleInput(DefaulModelClass):
    name: str = ''
    description: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'TenantRoleInput':
        return TenantRoleInput(**{key: obj.get(key, getattr(TenantRoleInput(), key)) for key in TenantRoleInput.__annotations__})


@dataclass
class TenantPermissionInput(DefaulModelClass):
    code: str = ''
    name: str = ''
    description: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'TenantPermissionInput':
        return TenantPermissionInput(**{key: obj.get(key, getattr(TenantPermissionInput(), key)) for key in TenantPermissionInput.__annotations__})


@dataclass
class TenantRolePermissionInput(DefaulModelClass):
    role_id: int = 0
    permission_id: int = 0

    @staticmethod
    def from_dict(obj: Any) -> 'TenantRolePermissionInput':
        return TenantRolePermissionInput(**{key: obj.get(key, getattr(TenantRolePermissionInput(), key)) for key in TenantRolePermissionInput.__annotations__})


@dataclass
class TenantLoginInput(DefaulModelClass):
    email: str = ''
    password: str = ''

    @staticmethod
    def from_dict(obj: Any) -> 'TenantLoginInput':
        return TenantLoginInput(**{key: obj.get(key, getattr(TenantLoginInput(), key)) for key in TenantLoginInput.__annotations__})


@dataclass
class TenantBootstrapInput(DefaulModelClass):
    company_code: str = ''
    company_document: str = ''
    corporate_name: str = ''
    fantasy_name: str = ''
    phone: str = ''
    email: str = ''
    zipcode: str = ''
    address: str = ''
    number: str = ''
    district: str = ''
    city: str = ''
    state: str = ''
    admin_name: str = ''
    admin_email: str = ''
    admin_password: str = ''

    @staticmethod
    def from_dict(obj: Any) -> 'TenantBootstrapInput':
        return TenantBootstrapInput(**{key: obj.get(key, getattr(TenantBootstrapInput(), key)) for key in TenantBootstrapInput.__annotations__})

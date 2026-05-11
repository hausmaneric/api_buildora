from dataclasses import dataclass
from typing import Any

from source.data.models.base import DefaultModelClass


@dataclass
class TenantCompanyInput(DefaultModelClass):
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
class TenantUserInput(DefaultModelClass):
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
class TenantRoleInput(DefaultModelClass):
    name: str = ''
    description: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'TenantRoleInput':
        return TenantRoleInput(**{key: obj.get(key, getattr(TenantRoleInput(), key)) for key in TenantRoleInput.__annotations__})


@dataclass
class TenantPermissionInput(DefaultModelClass):
    code: str = ''
    name: str = ''
    description: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'TenantPermissionInput':
        return TenantPermissionInput(**{key: obj.get(key, getattr(TenantPermissionInput(), key)) for key in TenantPermissionInput.__annotations__})


@dataclass
class TenantRolePermissionInput(DefaultModelClass):
    role_id: int = 0
    permission_id: int = 0

    @staticmethod
    def from_dict(obj: Any) -> 'TenantRolePermissionInput':
        return TenantRolePermissionInput(**{key: obj.get(key, getattr(TenantRolePermissionInput(), key)) for key in TenantRolePermissionInput.__annotations__})


@dataclass
class TenantBootstrapInput(DefaultModelClass):
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

from dataclasses import dataclass
from typing import Any
from models.nxm import DefaulModelClass


@dataclass
class AccountInput(DefaulModelClass):
    code: str = ''
    name: str = ''
    document: str = ''
    phone: str = ''
    email: str = ''
    status: int = 1
    plan_id: int | None = None
    database_url: str = ''
    database_host: str = ''
    database_port: int = 5432
    database_name: str = ''
    database_user: str = ''
    database_password: str = ''
    database_sslmode: str = 'prefer'
    storage_limit_mb: int = 0
    storage_used_mb: int = 0
    expiration_date: str | None = None
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'AccountInput':
        return AccountInput(**{key: obj.get(key, getattr(AccountInput(), key)) for key in AccountInput.__annotations__})


@dataclass
class PlanInput(DefaulModelClass):
    name: str = ''
    description: str = ''
    price: float = 0.0
    max_companies: int = 0
    max_users: int = 0
    max_works: int = 0
    max_storage_mb: int = 0
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'PlanInput':
        return PlanInput(**{key: obj.get(key, getattr(PlanInput(), key)) for key in PlanInput.__annotations__})


@dataclass
class ModuleInput(DefaulModelClass):
    code: str = ''
    name: str = ''
    description: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'ModuleInput':
        return ModuleInput(**{key: obj.get(key, getattr(ModuleInput(), key)) for key in ModuleInput.__annotations__})


@dataclass
class MasterUserInput(DefaulModelClass):
    name: str = ''
    login: str = ''
    password: str = ''
    email: str = ''
    phone: str = ''
    role: str = 'admin'
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'MasterUserInput':
        return MasterUserInput(**{key: obj.get(key, getattr(MasterUserInput(), key)) for key in MasterUserInput.__annotations__})


@dataclass
class AccountModuleInput(DefaulModelClass):
    account_id: int = 0
    module_id: int = 0
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'AccountModuleInput':
        return AccountModuleInput(**{key: obj.get(key, getattr(AccountModuleInput(), key)) for key in AccountModuleInput.__annotations__})

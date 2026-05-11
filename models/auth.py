from dataclasses import dataclass
from typing import Any
from models.nxm import DefaulModelClass


@dataclass
class Login(DefaulModelClass):
    email: str = ''
    password: str = ''

    @staticmethod
    def from_dict(obj: Any) -> 'Login':
        return Login(**{key: obj.get(key, getattr(Login(), key)) for key in Login.__annotations__})

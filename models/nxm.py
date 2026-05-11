from typing import Any
from dataclasses import dataclass
import json


class DefaulModelClass:
    def toJSON(self):
        data = {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith('_') and value is not None
        }
        return json.dumps(data, default=lambda o: o.__dict__, ensure_ascii=False, indent=4)


@dataclass
class BaseAuditModel(DefaulModelClass):
    created_at: str | None = None
    updated_at: str | None = None

    @staticmethod
    def from_dict(obj: Any) -> 'BaseAuditModel':
        return BaseAuditModel(**{key: obj.get(key, getattr(BaseAuditModel(), key)) for key in BaseAuditModel.__annotations__})

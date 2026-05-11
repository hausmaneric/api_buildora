from dataclasses import dataclass
from typing import Any

from source.data.models.base import DefaultModelClass


@dataclass
class ProductionEntryInput(DefaultModelClass):
    id: int = 0
    project_id: int = 0
    reference_date: str = ''
    service_name: str = ''
    unit: str = ''
    planned_quantity: float = 0.0
    executed_quantity: float = 0.0
    notes: str = ''
    created_by: int = 0

    @staticmethod
    def from_dict(obj: Any) -> 'ProductionEntryInput':
        return ProductionEntryInput(**{key: obj.get(key, getattr(ProductionEntryInput(), key)) for key in ProductionEntryInput.__annotations__})

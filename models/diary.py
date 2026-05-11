from dataclasses import dataclass
from typing import Any
from models.nxm import DefaulModelClass


@dataclass
class DailyLogFilter(DefaulModelClass):
    project_id: int | None = None
    status: str = ''
    created_by: int | None = None
    start_date: str | None = None
    end_date: str | None = None

    @staticmethod
    def from_dict(obj: Any) -> 'DailyLogFilter':
        return DailyLogFilter(**{key: obj.get(key, getattr(DailyLogFilter(), key)) for key in DailyLogFilter.__annotations__})


@dataclass
class DailyLogInput(DefaulModelClass):
    project_id: int = 0
    work_date: str = ''
    weather: str = ''
    summary: str = ''
    occurrences: str = ''
    status: str = 'draft'
    created_by: int = 0

    @staticmethod
    def from_dict(obj: Any) -> 'DailyLogInput':
        return DailyLogInput(**{key: obj.get(key, getattr(DailyLogInput(), key)) for key in DailyLogInput.__annotations__})


@dataclass
class DailyLogUpdateInput(DefaulModelClass):
    id: int = 0
    weather: str = ''
    summary: str = ''
    occurrences: str = ''
    status: str = 'draft'

    @staticmethod
    def from_dict(obj: Any) -> 'DailyLogUpdateInput':
        return DailyLogUpdateInput(**{key: obj.get(key, getattr(DailyLogUpdateInput(), key)) for key in DailyLogUpdateInput.__annotations__})

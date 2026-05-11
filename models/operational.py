from dataclasses import dataclass
from typing import Any
from models.nxm import DefaulModelClass


@dataclass
class ProjectInput(DefaulModelClass):
    id: int = 0
    name: str = ''
    code: str = ''
    client_name: str = ''
    company_id: int | None = None
    engineer_user_id: int | None = None
    address: str = ''
    number: str = ''
    district: str = ''
    city: str = ''
    state: str = ''
    zipcode: str = ''
    latitude: float | None = None
    longitude: float | None = None
    budget_amount: float = 0.0
    start_date: str | None = None
    end_date: str | None = None
    status: str = 'active'

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectInput':
        return ProjectInput(**{key: obj.get(key, getattr(ProjectInput(), key)) for key in ProjectInput.__annotations__})


@dataclass
class TeamInput(DefaulModelClass):
    id: int = 0
    project_id: int = 0
    name: str = ''
    description: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'TeamInput':
        return TeamInput(**{key: obj.get(key, getattr(TeamInput(), key)) for key in TeamInput.__annotations__})


@dataclass
class TeamMemberInput(DefaulModelClass):
    id: int = 0
    team_id: int = 0
    user_id: int | None = None
    member_name: str = ''
    role_name: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'TeamMemberInput':
        return TeamMemberInput(**{key: obj.get(key, getattr(TeamMemberInput(), key)) for key in TeamMemberInput.__annotations__})


@dataclass
class DailyOccurrenceInput(DefaulModelClass):
    id: int = 0
    daily_log_id: int = 0
    occurrence_type: str = ''
    title: str = ''
    description: str = ''
    severity: str = ''
    resolved: bool = False

    @staticmethod
    def from_dict(obj: Any) -> 'DailyOccurrenceInput':
        return DailyOccurrenceInput(**{key: obj.get(key, getattr(DailyOccurrenceInput(), key)) for key in DailyOccurrenceInput.__annotations__})


@dataclass
class DailyActivityInput(DefaulModelClass):
    id: int = 0
    daily_log_id: int = 0
    service_name: str = ''
    quantity: float = 0.0
    unit: str = ''
    location: str = ''
    notes: str = ''

    @staticmethod
    def from_dict(obj: Any) -> 'DailyActivityInput':
        return DailyActivityInput(**{key: obj.get(key, getattr(DailyActivityInput(), key)) for key in DailyActivityInput.__annotations__})


@dataclass
class DailyLaborInput(DefaulModelClass):
    id: int = 0
    daily_log_id: int = 0
    team_member_id: int | None = None
    worker_name: str = ''
    role_name: str = ''
    hours_worked: float = 0.0
    present: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'DailyLaborInput':
        return DailyLaborInput(**{key: obj.get(key, getattr(DailyLaborInput(), key)) for key in DailyLaborInput.__annotations__})


@dataclass
class DailyMaterialInput(DefaulModelClass):
    id: int = 0
    daily_log_id: int = 0
    material_name: str = ''
    movement_type: str = ''
    quantity: float = 0.0
    unit: str = ''
    notes: str = ''

    @staticmethod
    def from_dict(obj: Any) -> 'DailyMaterialInput':
        return DailyMaterialInput(**{key: obj.get(key, getattr(DailyMaterialInput(), key)) for key in DailyMaterialInput.__annotations__})


@dataclass
class DailyEquipmentInput(DefaulModelClass):
    id: int = 0
    daily_log_id: int = 0
    equipment_name: str = ''
    status: str = ''
    hours_used: float = 0.0
    notes: str = ''

    @staticmethod
    def from_dict(obj: Any) -> 'DailyEquipmentInput':
        return DailyEquipmentInput(**{key: obj.get(key, getattr(DailyEquipmentInput(), key)) for key in DailyEquipmentInput.__annotations__})


@dataclass
class DailyFileInput(DefaulModelClass):
    id: int = 0
    daily_log_id: int = 0
    file_name: str = ''
    file_type: str = ''
    file_url: str = ''
    file_size_bytes: int = 0
    notes: str = ''

    @staticmethod
    def from_dict(obj: Any) -> 'DailyFileInput':
        return DailyFileInput(**{key: obj.get(key, getattr(DailyFileInput(), key)) for key in DailyFileInput.__annotations__})


@dataclass
class DailySignatureInput(DefaulModelClass):
    id: int = 0
    daily_log_id: int = 0
    signed_by_user_id: int | None = None
    signer_name: str = ''
    signature_type: str = ''
    signature_data: str = ''

    @staticmethod
    def from_dict(obj: Any) -> 'DailySignatureInput':
        return DailySignatureInput(**{key: obj.get(key, getattr(DailySignatureInput(), key)) for key in DailySignatureInput.__annotations__})


@dataclass
class ProjectSetupMemberInput(DefaulModelClass):
    user_id: int | None = None
    member_name: str = ''
    role_name: str = ''
    active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectSetupMemberInput':
        return ProjectSetupMemberInput(**{key: obj.get(key, getattr(ProjectSetupMemberInput(), key)) for key in ProjectSetupMemberInput.__annotations__})


@dataclass
class ProjectSetupInput(DefaulModelClass):
    project_name: str = ''
    project_code: str = ''
    client_name: str = ''
    company_id: int | None = None
    engineer_user_id: int | None = None
    address: str = ''
    number: str = ''
    district: str = ''
    city: str = ''
    state: str = ''
    zipcode: str = ''
    latitude: float | None = None
    longitude: float | None = None
    budget_amount: float = 0.0
    start_date: str | None = None
    end_date: str | None = None
    status: str = 'active'
    main_team_name: str = 'Equipe Principal'
    main_team_description: str = ''
    members: list[dict] | None = None

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectSetupInput':
        return ProjectSetupInput(**{key: obj.get(key, getattr(ProjectSetupInput(), key)) for key in ProjectSetupInput.__annotations__})

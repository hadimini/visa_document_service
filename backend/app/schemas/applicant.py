from enum import Enum
from typing import Optional

from pydantic import Field

from app.models.applicants import Applicant
from app.schemas.core import ArchivedAtSchemaMixin, CoreSchema, IDSchemaMixin


class ApplicantGenderEnum(str, Enum):
    MALE = Applicant.GENDER_MALE
    FEMALE = Applicant.GENDER_FEMALE


class ApplicantBaseSchema(CoreSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[ApplicantGenderEnum] = None


class ApplicantCreateUpdateSchema(ApplicantBaseSchema):
    first_name: str
    last_name: str
    email: str
    gender: ApplicantGenderEnum


class ApplicantPublicSchema(ArchivedAtSchemaMixin, IDSchemaMixin, ApplicantBaseSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: Applicant.get_model_type())

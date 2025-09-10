from enum import Enum
from typing import Optional

from pydantic import Field

from app.models.applicants import Applicant
from app.schemas.core import ArchivedAtSchemaMixin, CoreSchema, IDSchemaMixin


class ApplicantGenderEnum(str, Enum):
    male = Applicant.GENDER_MALE
    female = Applicant.GENDER_FEMALE


class ApplicantBaseSchema(CoreSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[ApplicantGenderEnum] = None


class ApplicantCreateSchema(ApplicantBaseSchema):
    pass


class ApplicantUpdateSchema(ApplicantBaseSchema):
    pass


class ApplicantPublicSchema(ArchivedAtSchemaMixin, IDSchemaMixin, ApplicantBaseSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: Applicant.get_model_type())

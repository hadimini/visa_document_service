from typing import Optional

from pydantic import EmailStr

from app.schemas.core import CoreSchema


class PdfFileSchema(CoreSchema):
    name: str
    content: bytes
    content_type: str = "application/pdf"


class RecipientBodySchema(CoreSchema):
    title: str
    message: str
    btn_url: str
    btn_txt: str


class RecipientSchema(CoreSchema):
    email: EmailStr
    subject: str
    body: RecipientBodySchema
    cc_email: Optional[list[str]] = None
    attachments: Optional[list[PdfFileSchema]] = None

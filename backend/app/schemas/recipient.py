from typing import Optional

from pydantic import EmailStr

from app.schemas.core import CoreSchema


class PdfFileSchema(CoreSchema):
    name: str
    content: bytes
    content_type: str = "application/pdf"


class RecipientSchema(CoreSchema):
    email: EmailStr
    subject: str
    html: str
    cc_email: Optional[list[str]] = None
    attachments: Optional[list[PdfFileSchema]] = None

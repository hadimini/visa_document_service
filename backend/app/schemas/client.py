from typing import Annotated, Optional, Union

from pydantic import StringConstraints

from app.models.clients import Client
from app.schemas.core import CoreSchema, IDSchemaMixin


class ClientBaseSchema(CoreSchema):
    tariff_id: Optional[int] = None
    name: Optional[str] = None
    type: Union[Client.TYPE_INDIVIDUAL, Client.TYPE_LEGAL, None] = None


class ClientCreateSchema(CoreSchema):
    tariff_id: int
    name: Annotated[str, StringConstraints(min_length=3, max_length=100, pattern="^[a-zA-Z0-9 ]+$")]
    type: Union[Client.TYPE_INDIVIDUAL, Client.TYPE_LEGAL]


class ClientInDBSchema(IDSchemaMixin):
    pass


class ClientPublicSchema(IDSchemaMixin, ClientBaseSchema):
    pass

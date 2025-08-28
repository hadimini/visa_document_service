from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import class_mapper

from app.database.db import Base


class AbstractBaseModel(Base, AsyncAttrs):
    __abstract__ = True

    def to_dict(self) -> dict:
        """Converts SQLAlchemy object to dictionary"""
        columns = class_mapper(self.__class__).columns
        result = {column.key: getattr(self, column.key) for column in columns}
        return result

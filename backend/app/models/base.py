from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, class_mapper


class Base(DeclarativeBase, AsyncAttrs):

    def to_dict(self) -> dict:
        """Converts SQLAlchemy object to dictionary"""
        columns = class_mapper(self.__class__).columns
        result = {column.key: getattr(self, column.key) for column in columns}
        return result

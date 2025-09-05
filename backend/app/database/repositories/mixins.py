from abc import abstractmethod


class BuildFiltersMixin:
    @abstractmethod
    def build_filters(self, *, query_filters) -> list:
        """Build SQLAlchemy filter conditions from query filters"""
        pass

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator


class ChoiceType(TypeDecorator):
    impl = String

    def __init__(self, choices, **kwargs):
        self.choices = dict(choices)
        super().__init__(**kwargs)

    def process_bind_param(self, value, dialect):
        if value not in self.choices:
            raise ValueError(f"Invalid choice: {value}")
        return value

    def process_result_value(self, value, dialect):
        return value

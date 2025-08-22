from sqlalchemy.sql import func

from app.database.db import Base



class EmailConfirm(Base):
    table_name = "email_confirm"

#
# class PasswordResetConfirm(Base):
#     table_name = "password_reset_confirm"

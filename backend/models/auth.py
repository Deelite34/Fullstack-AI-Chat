import uuid

import bcrypt
from sqlalchemy import String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

import db


def make_uuid():
    return str(uuid.uuid4())


class User(db.Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    _password: Mapped[str]
    _salt: Mapped[str]
    activated: Mapped[bool] = mapped_column(default=False)
    activation_code: Mapped[str] = mapped_column(
        String(36), nullable=True, default=make_uuid
    )

    @hybrid_property
    def password(self):  # type: ignore
        return self._password

    def make_salted_hash(self, raw_password: str) -> str:
        """
        Hash raw password with salt and return the hashed password.
        If salt is not set, generate a new salt.
        """
        if not self._salt:
            self._salt = bcrypt.gensalt().decode("utf-8")

        pw_encoded = raw_password.encode("utf-8")
        salt_encoded = self._salt.encode("utf-8")
        return bcrypt.hashpw(pw_encoded, salt_encoded).decode("utf-8")

    @password.setter
    def password(self, value: str) -> None:
        """ Hash value and set it as password for model instance"""
        self._password = self.make_salted_hash(value)

    def verify_password(self, value: str) -> bool:
        """Hash raw password and verify against actual password. Return bool if password is valid"""
        pw_to_verify = self.make_salted_hash(value)
        return pw_to_verify == self._password

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
    _password: Mapped[str] = mapped_column()
    _salt: Mapped[str] = mapped_column()
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
        return self._make_salted_hash(raw_password, self._salt)

    @staticmethod
    def _make_salted_hash(raw_password: str, salt: str) -> str:
        """Encode input password with input salt and return the hashed password"""
        pw_encoded = raw_password.encode("utf-8")
        salt_encoded = salt.encode("utf-8")
        return bcrypt.hashpw(pw_encoded, salt_encoded).decode("utf-8")

    @password.setter  # type: ignore
    def password(self, password: str) -> None:
        """Hash value and set it as password for model instance"""
        self._password = self.make_salted_hash(password)

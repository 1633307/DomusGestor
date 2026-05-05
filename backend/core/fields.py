import hashlib
import hmac as _hmac_mod

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


def _fernet() -> Fernet:
    return Fernet(settings.FERNET_KEY.encode())


def encrypt_value(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        return ciphertext


def hmac_value(plaintext: str) -> str:
    """HMAC-SHA256 determinista per a cerques i unicitat."""
    return _hmac_mod.new(
        settings.FERNET_KEY.encode(),
        plaintext.encode(),
        hashlib.sha256,
    ).hexdigest()


class _EncryptedMixin:
    """Encripta el valor abans de guardar-lo i desencripta en llegir."""

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        return decrypt_value(value)

    def get_prep_value(self, value):
        parent = super().get_prep_value(value)
        if not parent:
            return parent
        return encrypt_value(parent)


class EncryptedCharField(_EncryptedMixin, models.TextField):
    pass


class EncryptedTextField(_EncryptedMixin, models.TextField):
    pass

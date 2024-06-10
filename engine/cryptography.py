import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def load_fernet():
    key = base64.urlsafe_b64encode(
        hashlib.sha256(settings.SECRET_KEY.encode()).digest()[:32]
    )
    return Fernet(key)


def encrypt(value):
    fernet = load_fernet()
    return fernet.encrypt(value.encode()).decode()


def decrypt(value):
    fernet = load_fernet()
    return fernet.decrypt(value.encode()).decode()

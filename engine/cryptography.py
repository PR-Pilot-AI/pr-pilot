import base64
import hashlib

from cryptography.fernet import Fernet

from django.conf import settings

key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest()[:32])
fernet = Fernet(key)


def encrypt(value):
    return fernet.encrypt(value.encode()).decode()


def decrypt(value):
    return fernet.decrypt(value.encode()).decode()

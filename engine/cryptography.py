import base64

from cryptography.fernet import Fernet

from django.conf import settings

fernet = Fernet(base64.b64encode(settings.SECRET_KEY[:32].encode()))


def encrypt(value):
    return fernet.encrypt(value.encode()).decode()


def decrypt(value):
    return fernet.decrypt(value).decode()

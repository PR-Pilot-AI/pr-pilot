import logging
import time

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings

logger = logging.getLogger(__name__)


# Generate a JWT token
def generate_jwt(app_id, private_key_path):
    logger.info(f"Generating JWT for app ID {app_id}")
    # Read the private key file
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # Generate the JWT
    now = int(time.time())
    payload = {
        # issued at time, 60 seconds in the past to allow for clock drift
        'iat': now - 60,
        # JWT expiration time (10 minute maximum)
        'exp': now + (5 * 60),
        # GitHub App's identifier
        'iss': app_id
    }

    encoded_jwt = jwt.encode(
        payload,
        private_key,
        algorithm='RS256'
    )

    return encoded_jwt


def get_installation_access_token(installation_id):
    logger.info(f"Getting installation token for installation ID {installation_id}")
    jwt_token = generate_jwt(int(settings.GITHUB_APP_ID), settings.PRIVATE_KEY_PATH)
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # Replace 'installation_id' with the ID of the app's installation
    installation_token_url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
    response = requests.post(installation_token_url, headers=headers)

    if response.status_code == 201:
        return response.json()['token']
    else:
        raise Exception(f"Failed to get installation token: {response.status_code}, {response.text}")


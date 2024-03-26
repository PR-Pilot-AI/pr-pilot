import datetime
import logging
import time
import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings

logger = logging.getLogger(__name__)

# Simple cache structure for storing installation tokens
installation_tokens_cache = {}


def generate_jwt(app_id, private_key_path):
    logger.info(f"Generating JWT for app ID {app_id}")
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    now = int(time.time())
    payload = {
        'iat': now - 60,
        'exp': now + (5 * 60),
        'iss': app_id
    }

    encoded_jwt = jwt.encode(
        payload,
        private_key,
        algorithm='RS256'
    )

    return encoded_jwt


def get_installation_access_token(installation_id):
    # Check cache first
    if installation_id in installation_tokens_cache:
        cached_token, expiry_time = installation_tokens_cache[installation_id]
        # If the cached token is still valid, return it
        if time.time() < expiry_time:
            logger.info(f"Using cached installation token for installation ID {installation_id}")
            return cached_token

    # Generate a new JWT token if no valid cached token is available
    jwt_token = generate_jwt(int(settings.GITHUB_APP_ID), settings.PRIVATE_KEY_PATH)
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    installation_token_url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
    logger.info(f"Requesting new installation token for installation ID {installation_id}")
    response = requests.post(installation_token_url, headers=headers)

    if response.status_code == 201:
        token_data = response.json()
        # Cache the new token along with its expiry time
        # GitHub tokens typically expire in 1 hour, but we'll subtract a small buffer (e.g., 2 minutes) to ensure we refresh in time
        # Date format: '2024-03-27T00:31:46Z'
        expires_at = datetime.datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
        expiry_time = expires_at.timestamp() - 120
        installation_tokens_cache[installation_id] = (token_data['token'], expiry_time)

        return token_data['token']
    else:
        raise Exception(f"Failed to get installation token: {response.status_code}, {response.text}")

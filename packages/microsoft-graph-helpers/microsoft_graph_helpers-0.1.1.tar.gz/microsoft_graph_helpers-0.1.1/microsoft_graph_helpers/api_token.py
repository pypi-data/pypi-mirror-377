import hashlib
import json
import logging
import requests
import time

# In-memory token cache
_token_cache = {}

def _generate_cache_key(tenant_id, client_id, secret, scope):
    key_string = f"{tenant_id}:{client_id}:{secret}:{scope}"
    return hashlib.sha256(key_string.encode()).hexdigest()

def get_bearer_token(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    scope: str = "https://graph.microsoft.com/.default"
) -> str:
    """
    Fetches a bearer token from Microsoft Identity Platform using client credentials.
    This function uses an in-memory cache to avoid redundant token requests.

    Args:
        tenant_id (str): Azure AD tenant ID.
        client_id (str): Application (client) ID.
        client_secret (str): Application secret.
        scope (str, optional): OAuth2 scope. Defaults to Microsoft Graph.

    Returns:
        str: Access token string.

    Raises:
        TokenRequestError: If the token request fails or returns a non-200 response.
        RuntimeError: If the response is not valid JSON or if the request times out.
    """
    logging.debug(f"get_bearer_token called for tenant_id={tenant_id[:5]}..., client_id={client_id[:5]}...")
    cache_key = _generate_cache_key(tenant_id, client_id, client_secret, scope)
    cached = _token_cache.get(cache_key)

    if cached and cached['expires_at'] > time.time():
        logging.debug(f"Retrieved cached Microsoft Graph token: {cache_key}")
        return cached['token']

    logging.debug(f"No valid cached Microsoft Graph token found for key: {cache_key}")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope,
        'grant_type': 'client_credentials'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(token_url, data=data, headers=headers, timeout=10)
        try:
            response_json = response.json()
        except ValueError:
            logging.critical("Non-JSON response received when retrieving Microsoft Graph token.")
            raise RuntimeError("Invalid JSON response received when retrieving Microsoft Graph token.")

        if response.status_code == 200:
            token = response_json.get('access_token')
            if not token:
                logging.critical("Microsoft Graph token not found in the response.")
                raise RuntimeError("Microsoft Graph token not found in the response.")

            expires_in = response_json.get('expires_in', 3599)
            _token_cache[cache_key] = {
                'token': token,
                'expires_at': time.time() + expires_in - 60
            }

            logging.debug(
                f"Obtained Microsoft Graph bearer token with expiry at {time.ctime(_token_cache[cache_key]['expires_at'])}."
            )
            return token

        error_dump = dict({'http_status_code': response.status_code}, **response_json)
        logging.critical(json.dumps(error_dump))
        raise TokenRequestError(json.dumps(error_dump, indent=4))

    except requests.exceptions.Timeout:
        logging.critical("Microsoft Graph token request timed out.")
        raise RuntimeError("Microsoft Graph token request timed out.")

class TokenRequestError(Exception):
    """Raised when a Microsoft Graph token request fails."""
    pass

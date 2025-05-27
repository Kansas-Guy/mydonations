# donations/sky_auth.py
import time, base64, requests, logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)
CACHE_KEY = 'bbms_access_token'

def get_bbms_access_token():
    """Return a valid SKY API bearer token, fetching & caching it if needed."""
    token_data = cache.get(CACHE_KEY)
    now = time.time()
    if token_data and token_data['expires_at'] > now + 60:
        return token_data['access_token']

    # Build Basic Auth header: base64(client_id:client_secret)
    creds = f"{settings.BB_CLIENT_ID}:{settings.BB_CLIENT_SECRET}".encode()
    b64_creds = base64.b64encode(creds).decode()
    headers = {
        'Authorization': f'Basic {b64_creds}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {'grant_type': 'refresh_token',
               'redirect_uri': 'http://localhost/oauth/callback',
               'refresh_token': settings.BB_REFRESH_TOKEN,
               'preserve_refresh_token': "true",
               'scope': settings.BB_OAUTH_SCOPES}

    resp = requests.post(settings.BB_TOKEN_URL, data=payload, headers=headers)

    if not resp.ok:
        logger.error(
            "OAuth token request failed: %s %s",
            resp.status_code, resp.text
        )
        resp.raise_for_status()

    data = resp.json()
    access_token = data['access_token']
    expires_in   = data.get('expires_in', 1800)  # default ~30m

    # Cache it so we don’t re-request every call
    cache.set(
      CACHE_KEY,
      {'access_token': access_token, 'expires_at': now + expires_in},
      timeout=expires_in
    )
    return access_token

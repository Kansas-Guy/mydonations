import json
import uuid
import time
import base64
import requests
import logging
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.urls import path

logger = logging.getLogger(__name__)

# ===== Views =====
def skyapi_authorize(request):
    logger.info("[authorize] in, GET params=%r", request.GET.dict())
    # 1) Generate CSRF-protection state
    state = uuid.uuid4().hex
    request.session['skyapi_state'] = state

    # 2) Read incoming params from the add-in front-end
    user_identity_token = request.GET.get('token')  # from args.getUserIdentityToken()
    env_id = request.GET.get('envid')              # from args.envId

    # 3) Build the redirect URI for your callback
    redirect_uri = settings.BB_REDIRECT_URI  # e.g. "https://yourapp.com/skyapi/oauth/callback"

    # 4) Construct the authorization URL
    params = {
        'response_type': 'code',
        'client_id': settings.BB_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'state': request.session['skyapi_state'],
        'environment_id': env_id,

    }

    from urllib.parse import urlencode
    auth_url = "https://oauth2.sky.blackbaud.com/connect/authorize?" + urlencode(params)
    logger.info("[authorize] redirecting to %s", auth_url)

    return redirect(auth_url)


def skyapi_callback(request):
    logger.info("[callback] query params=%r", request.GET.dict())
    code  = request.GET.get('code')
    state = request.GET.get('state')
    saved = request.session.get('skyapi_state')
    logger.info("[callback] code=%r, state=%r, saved_state=%r", code, state, saved)

    if not code or state != saved:
      logger.error("[callback] state mismatch or missing code")
      return HttpResponseBadRequest("Invalid OAuth state or missing code")

    # exchange
    creds     = f"{settings.BB_CLIENT_ID}:{settings.BB_CLIENT_SECRET}".encode()
    b64_creds = base64.b64encode(creds).decode()
    headers   = {'Authorization': f"Basic {b64_creds}",
                 'Content-Type':  'application/x-www-form-urlencoded'}
    payload   = {'grant_type': 'authorization_code',
                 'code':        code,
                 'redirect_uri': settings.BB_REDIRECT_URI}

    logger.info("[callback] POST %s with payload %r", settings.BB_TOKEN_URL, payload)
    token_resp = requests.post(settings.BB_TOKEN_URL, data=payload, headers=headers)
    token_resp.raise_for_status()
    token_data = token_resp.json()
    logger.info("[callback] token_data received (first 20 chars)=%r", token_data['access_token'][:20])

    request.session['sky_api_token']     = token_data['access_token']
    request.session['sky_token_expires'] = time.time() + token_data['expires_in']

    # close popup
    return HttpResponse("""
      <!DOCTYPE html><html><body>
      <script>
        // tell the opener “here’s your token”
        window.opener.postMessage(
          { accessToken: "%s" },
          "%s"
        );
        window.close();
      </script>
      </body></html>
    """ % (token_data['access_token'], request.scheme + "://" + request.get_host()))

def skyapi_token(request):
    token   = request.session.get('sky_api_token')
    expires = request.session.get('sky_token_expires', 0)
    logger.info("[token] session token=%r expires=%r", token and token[:10], expires)

    if not token or expires < time.time():
      logger.warning("[token] no valid token in session")
      return JsonResponse({'error': 'no token'}, status=401)

    return JsonResponse({'accessToken': token})


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
    """
    Kick off the SKY API OAuth flow by generating a state and redirecting
    the user to Blackbaud's authorization endpoint.
    """
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
    auth_url = f"https://app.blackbaud.com/oauth/authorize?{urlencode(params)}"

    return redirect(auth_url)


def skyapi_callback(request):
    """
    Handle the OAuth callback: validate state, exchange code for tokens,
    then close the popup.
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    logger.info(f"[skyapi_callback] code={code!r}, state={state!r}, session_stat={request.session.get('skyapi_state')!r}")
    error = request.GET.get('error')
    if error:
        return HttpResponse(f"<h1>OAuth Error</h1><p>{error}</p>")

    code = request.GET.get('code')
    state = request.GET.get('state')
    saved = request.session.get('skyapi_state')
    if not code or not state or state != saved:
        return HttpResponseBadRequest('Invalid OAuth state or missing code.')

    # Exchange the authorization code for tokens
    creds = f"{settings.BB_CLIENT_ID}:{settings.BB_CLIENT_SECRET}".encode()
    b64_creds = base64.b64encode(creds).decode()
    headers = {
        'Authorization': f'Basic {b64_creds}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.BB_REDIRECT_URI,
    }
    token_resp = requests.post(settings.BB_TOKEN_URL, data=payload, headers=headers)
    token_resp.raise_for_status()
    token_data = token_resp.json()

    request.session["sky_api_token"] = token_data['access_token']
    request.session["sky_token_expires"] = time.time() + token_data.get("expires_in", 3600)

    logger.info("[skyapi_callback] stored access_token (first 10 chars)=%r expires=%r",
                token_data["access_token"], request.session["sky_token_expires"])

    # '<script>window.close();</script>'
    # Render a tiny HTML page that closes the popup
    return HttpResponse(f"""
        <!DOCTYPE html><html><body> 
        <script>
            localStorage.setItem(
            'skyapi_token_data',
            JSON.stringify({json.dumps(token_data)})
            );
            window.close();
        </script>
        </body></html>
    """, content_type="text/html")

def skyapi_token(request):
    token = request.session.get('sky_api_token')
    expires = request.session.get('sky_token_expires', 0)

    if not token or expires < time.time():
        return JsonResponse({'error': 'no token'}, status=401)
    return JsonResponse({ "accessToken": token })


import requests
from requests.auth import HTTPBasicAuth

url = 'https://oauth2.sky.blackbaud.com/token'
auth = HTTPBasicAuth('95fdf99e-71d9-4cc1-872c-4536e47a57b3', 'ksmLjGXsodddo3hoHtHcCHyV0arrXVMrXCHquO/7FPk=')
data = {
  'grant_type':    'authorization_code',
  'code':          '88fac2ce64dc481da753785fbb9e8dc0',
  'redirect_uri':  'http://localhost/oauth/callback'
}
resp = requests.post(url, auth=auth, data=data)
print(resp.status_code, resp.text)
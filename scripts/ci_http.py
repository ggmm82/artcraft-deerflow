"""Exercise the real DeerFlow auth/CSRF middleware and Studio over the proxy."""
import http.cookiejar
import json
import os
import urllib.request

base = 'http://127.0.0.1:2026'
passwords = urllib.request.HTTPPasswordMgrWithDefaultRealm()
passwords.add_password(None, base, 'admin', os.environ['STUDIO_PASSWORD'])
cookies = http.cookiejar.CookieJar()
client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies),
                                    urllib.request.HTTPBasicAuthHandler(passwords))


def request(path, payload=None, method=None):
    headers = {'Origin': base, 'Content-Type': 'application/json'}
    for cookie in cookies:
        if cookie.name == 'csrf_token':
            headers['X-CSRF-Token'] = cookie.value
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    with client.open(req, timeout=30) as response:
        return response.read()


request('/api/v1/auth/initialize', {'email': 'studio-ci@example.com',
                                   'password': 'CiOnly-Strong-Login-P4ssword!78239'})
assert any(cookie.name == 'access_token' for cookie in cookies)
assert b'ArtCraft Studio' in request('/studio/')
catalog = json.loads(request('/studio/api/catalog'))
assert set(catalog['agents']) == {app['id'] for app in catalog['applications']}
saved = json.loads(request('/studio/api/agents/gridcraft',
                          {'engine': 'gemini', 'model': '', 'instructions': 'Preferisci euro',
                           'enabled': True}, method='PUT'))
assert saved['engine'] == 'gemini'
catalog = json.loads(request('/studio/api/catalog'))
assert catalog['agents']['gridcraft']['instructions'] == 'Preferisci euro'
assert b'ArtCraft Studio' in request('/workspace/studio')
print('OK: account DeerFlow, sessione, CSRF, pannello, configurazione specialisti e pagina integrata.')

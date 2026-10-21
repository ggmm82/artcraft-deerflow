"""Exercise the real DeerFlow auth/CSRF middleware and Studio over the proxy."""
import http.cookiejar
import json
import os
import urllib.request
import urllib.error

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
# Native Agent management and managed capabilities must be available after login.
json.loads(request('/api/agents'))
skills = json.loads(request('/api/skills'))['skills']
assert any(s['name'] == 'artcraft-blender' and s['category'] == 'integrations' for s in skills)
assert len({s['name'] for s in skills}) == len(skills)
request('/api/agents', {'name':'ci-native-profile','description':'Native capability scope','skills':['artcraft-freecad']})
profile = json.loads(request('/api/agents/ci-native-profile'))
assert profile['skills'] == ['artcraft-freecad']
request('/api/agents/ci-native-profile', method='DELETE')
request('/api/skills/artcraft-blender', {'enabled':False}, method='PUT')
assert json.loads(request('/studio/api/catalog'))['agents']['blender']['enabled'] is False
request('/api/skills/artcraft-blender', {'enabled':True}, method='PUT')
assert json.loads(request('/studio/api/catalog'))['agents']['blender']['enabled'] is True


catalog = json.loads(request('/studio/api/catalog'))
assert set(catalog['agents']) == {app['id'] for app in catalog['applications']}
saved = json.loads(request('/studio/api/agents/gridcraft',
                          {'engine': 'gemini', 'model': '', 'instructions': 'Preferisci euro',
                           'enabled': True}, method='PUT'))
assert saved['engine'] == 'gemini'
catalog = json.loads(request('/studio/api/catalog'))
assert catalog['agents']['gridcraft']['instructions'] == 'Preferisci euro'
assert b'La tua squadra' in request('/workspace/studio')
request('/api/v1/auth/logout', {})
request('/api/v1/auth/register', {'email': 'studio-ci-user@example.com',
                                 'password': 'CiOnly-Regular-User-P4ssword!78239'})
for path, payload, method in [('/studio/api/catalog', None, 'GET'),
                              ('/studio/api/login/gemini', {}, 'POST'),
                              ('/studio/api/team', {'engine': 'gemini'}, 'PUT')]:
    try:
        request(path, payload, method)
    except urllib.error.HTTPError as error:
        assert error.code == 403, (path, error.code)
    else:
        raise AssertionError('Un utente ordinario ha accesso alla configurazione globale: ' + path)
print('OK: account, sessione, CSRF, configurazione amministratore; accesso globale negato agli utenti ordinari.')

"""Apply shared team routing and keep submitted work alive after browser disconnect."""
import json
import re

RUN_PATH = re.compile(r'^/api/(?:threads/[^/]+/)?runs(?:/(?:stream|wait))?/?$')


def shared_run(body):
    if not isinstance(body, dict):
        return body
    result = dict(body)
    # Missing browser options must not inherit the Gateway's cancel default.
    # An explicit API cancellation policy remains supported; Stop uses its own endpoint.
    result.setdefault('on_disconnect', 'continue')
    result['context'] = {**(body.get('context') or {}), 'model_name': 'studio-codex'}
    config = dict(body.get('config') or {})
    if isinstance(config.get('configurable'), dict) and 'model_name' in config['configurable']:
        config['configurable'] = {**config['configurable'], 'model_name': 'studio-codex'}
        result['config'] = config
    return result


class TeamRoutingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        path, method = scope.get('path', ''), scope.get('method')
        if method == 'POST' and RUN_PATH.fullmatch(path):
            chunks = []
            while True:
                message = await receive()
                if message['type'] != 'http.request':
                    return
                chunks.append(message.get('body', b''))
                if not message.get('more_body'):
                    break
            body = b''.join(chunks)
            try:
                body = json.dumps(shared_run(json.loads(body))).encode()
            except (ValueError, TypeError):
                pass  # Native request validation reports malformed input.
            scope = {**scope, 'headers': [(k, v) for k, v in scope['headers'] if k != b'content-length']}
            scope['headers'].append((b'content-length', str(len(body)).encode()))
            consumed = False
            original_receive = receive
            async def replaced_receive():
                nonlocal consumed
                if not consumed:
                    consumed = True
                    return {'type': 'http.request', 'body': body, 'more_body': False}
                return await original_receive()
            receive = replaced_receive
        if method == 'GET' and path.rstrip('/') == '/api/models':
            start, chunks = None, []
            original_send = send
            async def filtered_send(message):
                nonlocal start
                if message['type'] == 'http.response.start':
                    start = message
                elif message['type'] == 'http.response.body':
                    chunks.append(message.get('body', b''))
                    if message.get('more_body'):
                        return
                    body = b''.join(chunks)
                    if start['status'] == 200:
                        try:
                            data = json.loads(body)
                            data['models'] = [m for m in data.get('models', []) if m.get('name') == 'studio-codex']
                            body = json.dumps(data).encode()
                        except (ValueError, TypeError, KeyError):
                            pass
                    headers = [(k, v) for k, v in start['headers'] if k != b'content-length']
                    await original_send({**start, 'headers': [*headers, (b'content-length', str(len(body)).encode())]})
                    await original_send({'type': 'http.response.body', 'body': body})
            send = filtered_send
        await self.app(scope, receive, send)

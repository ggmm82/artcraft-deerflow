"""Lossless function-call exchange with the official Gemini CLI content generator."""
import json
import re
import uuid


def parts(content):
    if isinstance(content, str):
        return [{'text': content}] if content else []
    result = []
    for block in content or []:
        if isinstance(block, str):
            result.append({'text': block})
        elif block.get('type') in ('text', 'text_delta'):
            result.append({'text': block.get('text', '')})
        elif block.get('type') == 'image_url':
            url = block['image_url']
            url = url.get('url', '') if isinstance(url, dict) else url
            match = re.fullmatch(r'data:(image/[\w.+-]+);base64,(.+)', url, re.S)
            if not match:
                raise ValueError('Gemini richiede immagini incorporate, non URL remoti')
            result.append({'inlineData': {'mimeType': match[1], 'data': match[2]}})
        elif block.get('type') == 'image' and (block.get('base64') or block.get('source_type') == 'base64'):
            result.append({'inlineData': {'mimeType': block.get('mime_type', 'image/png'),
                                         'data': block.get('base64') or block.get('data')}})
        else:
            raise ValueError('Contenuto multimodale Gemini non supportato')
    return result


def request(messages, model, tools=(), tool_choice=None):
    contents, system, names = [], [], {}
    for message in messages:
        kind = message['type']
        if kind in ('system', 'developer'):
            system.extend(parts(message['content']))
            continue
        if kind == 'tool':
            identifier = message['tool_call_id']
            name = names.get(identifier)
            if not name:
                raise ValueError('Risultato Gemini senza chiamata corrispondente')
            value = message['content']
            try:
                value = json.loads(value) if isinstance(value, str) else value
            except ValueError:
                pass
            data = [{'functionResponse': {'id': identifier, 'name': name,
                                         'response': {'result': value}}}]
        elif kind == 'ai':
            calls = message.get('tool_calls', [])
            names.update({call['id']: call['name'] for call in calls})
            data = message.get('gemini_parts') or (parts(message['content']) + [
                {'functionCall': {'id': c['id'], 'name': c['name'], 'args': c['args']}} for c in calls])
            # Official Gemini CLI uses this sentinel for synthetic/foreign tool
            # history. It permits switching a saved Codex/DeepSeek conversation.
            data = [{**part, 'thoughtSignature': part.get('thoughtSignature') or
                     'skip_thought_signature_validator'} if 'functionCall' in part else part for part in data]
        elif kind == 'human':
            data = parts(message['content'])
        else:
            raise ValueError('Tipo di messaggio Gemini non supportato')
        role = 'model' if kind == 'ai' else 'user'
        if not data:
            continue
        if contents and contents[-1]['role'] == role:
            contents[-1]['parts'].extend(data)
        else:
            contents.append({'role': role, 'parts': data})
    config = {'systemInstruction': {'parts': system}} if system else {}
    if tools:
        config['tools'] = [{'functionDeclarations': [
            {'name': t['function']['name'], 'description': t['function'].get('description', ''),
             'parametersJsonSchema': t['function'].get('parameters', {'type': 'object'})} for t in tools]}]
        if isinstance(tool_choice, dict):
            chosen = tool_choice.get('function', {}).get('name')
            if chosen not in {t['function']['name'] for t in tools}:
                raise ValueError('Strumento Gemini richiesto non disponibile')
            policy = {'mode': 'ANY', 'allowedFunctionNames': [chosen]}
        else:
            mode = {'auto': 'AUTO', 'none': 'NONE', 'required': 'ANY', 'any': 'ANY'}.get(tool_choice or 'auto')
            if mode is None:
                raise ValueError('Scelta degli strumenti Gemini non valida')
            policy = {'mode': mode}
        config['toolConfig'] = {'functionCallingConfig': policy}
    return {'model': model, 'contents': contents, 'config': config}


def response(value, tools=()):
    candidates = value.get('candidates', [])
    if not candidates:
        raise RuntimeError('Gemini non ha restituito una risposta utilizzabile')
    candidate = candidates[0]
    if candidate.get('finishReason') not in (None, 'STOP'):
        raise RuntimeError('Risposta Gemini incompleta o bloccata: ' + str(candidate['finishReason']))
    raw = candidate.get('content', {}).get('parts', [])
    allowed = {t['function']['name'] for t in tools}
    calls, text = [], []
    for part in raw:
        if part.get('thought'):
            continue
        if 'text' in part:
            text.append(part['text'])
        if 'functionCall' in part:
            call = part['functionCall']
            if call.get('name') not in allowed or not isinstance(call.get('args', {}), dict):
                raise RuntimeError('Chiamata Gemini non valida o non autorizzata')
            identifier = call.get('id') or 'gemini-' + uuid.uuid4().hex
            call['id'] = identifier
            calls.append({'id': identifier, 'name': call['name'], 'args': call.get('args', {}), 'type': 'tool_call'})
    if not calls and not text:
        raise RuntimeError('Risposta Gemini vuota')
    return {'content': ''.join(text), 'tool_calls': calls, 'gemini_parts': raw}

"""Tool-independent acceptance contract, grounded in actual user messages."""
import hashlib
import json

METHODS = {'content', 'visual', 'listening', 'structural', 'functional', 'reference', 'technical'}


def capabilities(engine):
    return {'content': True, 'structural': True, 'functional': True, 'reference': True,
            'technical': True, 'visual': engine in ('codex', 'gemini'), 'listening': False}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def contract(requests, criteria=None):
    criteria = criteria or []
    if not isinstance(criteria, list) or len(criteria) > 20:
        raise ValueError('Usa al massimo 20 requisiti osservabili')
    rules = [{'id': 'request_fidelity', 'requirement': 'Il risultato soddisfa la richiesta originale e le modifiche dell’utente, senza sostituzioni arbitrarie.',
              'method': 'content', 'critical': True, 'reference_paths': []}]
    seen = {'request_fidelity'}
    for item in criteria:
        if isinstance(item, dict) and item.get('id') == 'request_fidelity':
            continue  # The coordinator cannot weaken the runtime-owned criterion.
        if (not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'].replace('_', '').isalnum()
                or len(item['id']) > 60 or item['id'] in seen or not isinstance(item.get('requirement'), str)
                or not item['requirement'].strip() or item.get('method') not in METHODS
                or not isinstance(item.get('reference_paths', []), list)
                or any(not isinstance(p, str) for p in item.get('reference_paths', []))):
            raise ValueError('Ogni requisito richiede id unico, requirement, method e reference_paths opzionali')
        seen.add(item['id'])
        origin = item.get('origin', 'unspecified')
        quote = item.get('source_quote', '')
        if origin not in ('user', 'proposal', 'unspecified') or not isinstance(quote, str) or len(quote) > 600:
            raise ValueError('Origine del criterio: user, proposal o unspecified; source_quote entro 600 caratteri')
        if origin == 'user' and (not quote.strip() or not any(quote in text for text in requests)):
            raise ValueError('Un vincolo attribuito all’utente richiede source_quote presente nei suoi messaggi reali')
        rules.append({'id': item['id'], 'requirement': item['requirement'][:1000], 'method': item['method'],
                      'critical': item.get('critical', True) is not False, 'reference_paths': item.get('reference_paths', [])[:10]})
        if 'origin' in item or 'source_quote' in item:
            rules[-1].update(origin=origin, source_quote=quote)
    value = {'user_requests': requests[:1] + requests[-8:] if len(requests) > 9 else requests,
             'criteria': rules}
    return {**value, 'hash': fingerprint(value)}


def evaluate(criteria, acceptance, engine):
    """Check coverage and observability; do not pretend to judge taste in Python."""
    result = [dict(c) for c in criteria]
    for c in result:
        # No supported audio observation path is wired into these transports.
        # Shell measurements and generating a waveform are structural evidence.
        if not capabilities(engine).get(c.get('method'), False):
            c.update(status='not_run', evidence='Questa modalità di osservazione non è disponibile nel collegamento del modello; le misure tecniche non la sostituiscono.')
    if acceptance:
        for rule in acceptance['criteria']:
            matches = [c for c in result if c.get('requirement_id') == rule['id']]
            if not matches:
                result.append({'requirement_id': rule['id'], 'criterion': rule['requirement'], 'method': rule['method'],
                               'status': 'not_run', 'critical': rule['critical'], 'evidence': 'Il rapporto non verifica questo requisito della richiesta.'})
                continue
            for c in matches:
                c['critical'] = rule['critical']
                if rule['method'] != 'content' and c.get('method') != rule['method']:
                    c.update(status='not_run', evidence='Il metodo usato non verifica il requisito concordato.')
                if rule['id'] == 'request_fidelity' and c.get('method') == 'technical':
                    c.update(status='not_run', evidence='Decodifica, formato o esistenza del file non provano la rispondenza alla richiesta.')
                if rule['method'] == 'reference' and not rule['reference_paths']:
                    c.update(status='not_run', evidence='Il riferimento necessario non è disponibile: non sostituirlo senza l’utente.')
        relevant = [c for c in result if c.get('critical', True)]
    else:
        relevant = result
    status = 'needs_revision' if any(c['status'] == 'failed' for c in relevant) else 'passed' if relevant and all(c['status'] == 'passed' for c in relevant) else 'needs_review'
    return result, status

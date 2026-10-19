"""Preserve actionable review feedback and bind before/after claims to files."""
from pathlib import Path

try:
    from .acceptance import capabilities
except ImportError:
    from acceptance import capabilities

STRATEGIES = {'revise', 'change_method', 'verify', 'missing_dependency'}


def actions(value, criteria):
    raw = value.get('revision_actions')
    legacy = raw is None
    if legacy:
        raw = value.get('targeted_corrections', [])
    if not isinstance(raw, list) or len(raw) > 12:
        raise ValueError('Revisione: al massimo 12 azioni di correzione concrete')
    known = {c.get('requirement_id') for c in criteria if c.get('requirement_id')}
    result = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError('Azione di correzione non valida')
        rid, action = item.get('requirement_id', ''), item.get('action', '')
        strategy, priority = item.get('strategy', 'revise'), item.get('priority', 2)
        reason = item.get('reason', '')
        if (not isinstance(rid, str) or rid and rid not in known or not isinstance(action, str)
                or not action.strip() or len(action) > 1200 or not isinstance(reason, str) or len(reason) > 1200
                or not isinstance(strategy, str) or strategy not in STRATEGIES or type(priority) is not int or priority not in (1, 2, 3)):
            raise ValueError('Correzione: requisito esistente, azione concreta, strategia e priorità 1–3')
        result.append({'requirement_id': rid, 'action': action.strip(), 'reason': reason,
                       'strategy': strategy, 'priority': priority})
    return sorted(result, key=lambda a: a['priority'])


def comparison(value, criteria, handoff, workspace, target, digest, engine):
    baseline = value.get('baseline_path')
    if not baseline:
        if value.get('comparison'):
            raise ValueError('Il confronto richiede baseline_path effettivamente letto')
        return None
    if not isinstance(baseline, str):
        raise ValueError('baseline_path deve essere un percorso')
    root = Path(workspace).resolve(); path = Path(baseline).resolve()
    if (not path.is_relative_to(root) or path == target or not path.is_file()
            or str(path) not in handoff['source_files']):
        raise ValueError('Confronto: versione precedente distinta, esistente e letta in source_files')
    before, after = digest(path), digest(target)
    items = value.get('comparison', [])
    if not isinstance(items, list) or not 1 <= len(items) <= 20:
        raise ValueError('Confronto: da 1 a 20 requisiti osservati prima/dopo')
    known = {c.get('requirement_id'): c for c in criteria if c.get('requirement_id')}
    result, seen = [], set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError('Confronto non valido')
        rid, status = item.get('requirement_id'), item.get('status')
        evidence = item.get('evidence')
        if (not isinstance(rid, str) or rid not in known or rid in seen or status not in ('improved', 'unchanged', 'regressed', 'not_verified')
                or not isinstance(evidence, str) or not evidence.strip() or len(evidence) > 2000):
            raise ValueError('Confronto: requisito unico esistente, stato e prova concreta obbligatori')
        seen.add(rid)
        if status == 'improved' and before == after:
            raise ValueError('Non dichiarare migliorato un prodotto con byte identici alla versione precedente')
        criterion = known[rid]
        if not capabilities(engine).get(criterion.get('method'), False) or criterion.get('status') == 'not_run':
            status = 'not_verified'
            evidence = 'Metodo di osservazione non eseguito o non disponibile; il miglioramento non è verificato.'
        result.append({'requirement_id': rid, 'status': status, 'evidence': evidence})
    return {'baseline_path': str(path), 'baseline_sha256': before, 'product_sha256': after,
            'criteria': result, 'note': 'Confronto dello specialista su file identificati; non certificazione oggettiva di qualità.'}

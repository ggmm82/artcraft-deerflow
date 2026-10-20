"""Bounded control replies: execution success never hides a failed deliverable.

Full runtime results remain scoped, immutable and addressable. This projection
is for LLM control messages; the browser keeps the full project API.
"""
import json

from .acceptance import fingerprint
from .project_skills import redact_memory, scoped_file
from .progress import clean_summary

LIMIT = 8000  # Below pinned DeerFlow's 12,000-character synopsis threshold.


def counts(items):
    return {status: sum(x.get('status') == status for x in items) for status in ('passed', 'failed', 'not_run')}


def decision(result):
    review = result.get('quality_review') or {}
    delivery = result.get('delivery') or {}
    checks = result.get('checks', [])
    if not result.get('ok'):
        return 'execution_failed'
    if (delivery.get('technical_status') == 'needs_revision' or delivery.get('issues')
            or review.get('status') in ('failed', 'needs_revision') or result.get('check_counts', {}).get('failed', 0) or any(c.get('status') == 'failed' for c in checks)):
        return 'needs_revision'
    if review.get('status') == 'passed':
        return 'review_passed'
    return 'review_required' if result.get('outputs') else 'work_complete'


def project_view(project):
    if not project or project.get('archived'):
        return project
    value = {k: project.get(k) for k in ('id', 'status', 'summary', 'next_action', 'product_path',
             'quality_status', 'attention', 'outcome', 'memory', 'requirements', 'project_type')}
    value['brief'] = clean_summary(project.get('brief'), 500)
    acceptance = project.get('acceptance') or {}
    value['acceptance'] = {k: acceptance.get(k) for k in ('hash', 'request_count', 'request_manifest')}
    value['acceptance']['criteria'] = [{k: c.get(k) for k in ('id', 'method', 'critical', 'origin')} |
            {'requirement': clean_summary(c.get('requirement'), 160)} for c in acceptance.get('criteria', [])]
    orientation = project.get('orientation') or {}
    value['orientation'] = {k: orientation.get(k) for k in ('total', 'counts', 'current', 'needs_briefing', 'history_count')}
    active = set(orientation.get('active_step_ids', [s['id'] for s in project.get('steps', [])]))
    value['steps'] = [{k: s.get(k) for k in ('id', 'agent', 'role_id', 'status')} |
            {'goal': clean_summary(s.get('goal'), 180)} for s in project.get('steps', []) if s['id'] in active][:16]
    value['roles'] = [{k: r.get(k) for k in ('id', 'title', 'tools', 'skill', 'experience')} |
            {'mission': clean_summary(r.get('mission'), 160)} for r in project.get('roles', [])][:12]
    value['results'] = [{k: r.get(k) for k in ('path', 'role', 'delivery_id')} for r in project.get('results', [])[:4]]
    value['deliveries'] = [{k: d.get(k) for k in ('id', 'title', 'technical_status', 'current')} for d in project.get('deliveries', [])[:3]]
    value['revision_actions'] = [fit(a, 160) for a in project.get('revision_actions', [])[:3]]
    value['revision_action_count'] = len(project.get('revision_actions', []))
    value['comparison'] = fit(project.get('comparison'), 120)
    strategy = project.get('strategy') or {}
    value['strategy'] = {k: strategy.get(k) for k in ('state', 'method', 'reason', 'user_action', 'stop_reason', 'record')}
    value['strategy']['alternatives'] = [fit(a, 160) for a in strategy.get('alternatives', [])]
    value['method_recovery'] = project.get('method_recovery')
    product = next((r for r in project.get('results', []) if r.get('path') == project.get('product_path')), None)
    if product and project.get('status') in ('review', 'blocked', 'ready'):
        sources = [r for r in project.get('results', []) if product.get('delivery_id')
                   and r.get('delivery_id') == product['delivery_id'] and r.get('role') in ('source_archive', 'editable_source')]
        sources.sort(key=lambda r: r.get('role') != 'source_archive')
        value['presentation'] = {'paths': list(dict.fromkeys([product['path'], *[s['path'] for s in sources[:2]]])),
            'instruction': 'Prima di terminare o mettere in pausa il turno, chiama present_files sui file utili indicati. '
                'Se non approvati, etichettali come bozza/studio incompleto e spiega i difetti. La presenza nel pannello '
                'Progetto non sostituisce present_files e non dimostra il completamento del risultato richiesto.'}
    return value


def delegate_view(result):
    # Preserve existing top-level fields on ordinary small replies.
    value = dict(result)
    value['decision'] = decision(result)
    review = result.get('quality_review') or {}
    value['check_counts'] = result.get('check_counts', counts(result.get('checks', [])))
    value['review_counts'] = counts(review.get('criteria', []))
    value['next_action'] = (review.get('revision_actions') or [{}])[0].get('action', '')
    if review.get('status') == 'needs_revision':
        value['revision_instruction'] = ('Trasforma le correzioni in un incarico mirato sui file esistenti e verifica il prima/dopo. '
            'Non chiedere un altro procedi per una correzione già nello scopo autorizzato. Se il metodo non migliora, '
            'prova un metodo diverso pertinente; per dipendenze realmente mancanti spiega il limite. Non moltiplicare '
            'produzione o rigenerare parti già valide.')
    return value


def fit(value, limit=280):
    """Shrink descriptions, never file identities or status/requirement IDs."""
    if isinstance(value, str):
        return clean_summary(value, limit)
    if isinstance(value, list):
        return [fit(x, limit) for x in value]
    if isinstance(value, dict):
        identities = {'path', 'product_path', 'baseline_path', 'handoff_path', 'output_dir', 'details_path', 'report_path',
                      'id', 'requirement_id', 'role_id', 'delivery_id', 'sha256', 'details_sha256', 'verified_products', 'available_files', 'method_recovery', 'presentation'}
        return {k: v if k in identities else fit(v, limit) for k, v in value.items()}
    return value


def reply(workspace, payload, kind):
    full = redact_memory(payload)
    text = json.dumps(full, ensure_ascii=False)
    reference = scoped_file(workspace, 'control-results/' + kind + '-' + fingerprint(full) + '.json', text)
    value = {'project': project_view(full.get('project'))} if kind == 'plan' else delegate_view(full)
    value.update(details_path=reference['path'], details_sha256=reference['sha256'])
    if len(json.dumps(value, ensure_ascii=False)) <= LIMIT:
        return json.dumps(value, ensure_ascii=False)
    value = fit(value)
    if kind == 'delegate':
        # Put verdicts before inventories, not after pages of opening instructions.
        review = full.get('quality_review') or {}
        value['quality_review'] = {k: review.get(k) for k in ('status', 'product_path', 'report_path')}
        value['quality_review']['revision_actions'] = [fit(a, 160) for a in review.get('revision_actions', [])[:3]]
        value['quality_review']['revision_action_count'] = len(review.get('revision_actions', []))
        value['quality_review']['comparison'] = fit(review.get('comparison'), 120)
        value['quality_review']['criteria'] = [{k: c.get(k) for k in ('requirement_id', 'status', 'method')} |
            {'evidence': clean_summary(c.get('evidence'), 120)} for c in review.get('criteria', [])]
        value['outputs'] = [{k: f.get(k) for k in ('path', 'role', 'format')} for f in full.get('outputs', [])[:4]]
        value['output_count'] = full.get('output_count', len(full.get('outputs', [])))
        value['checks'] = sorted(value.get('checks', []), key=lambda c: c.get('status') == 'passed')[:5]
        value['warnings'] = value.get('warnings', [])[:3]
        value['review_notes'] = value.get('review_notes', [])[:4]
        value['available_files'] = value.get('available_files', [])[:4]
    for limit in (160, 80):
        if len(json.dumps(value, ensure_ascii=False)) <= LIMIT:
            break
        value = fit(value, limit)
        if kind == 'plan':
            for key in ('roles', 'steps', 'results'):
                value['project'][key] = value['project'].get(key, [])[:4]
    if len(json.dumps(value, ensure_ascii=False)) > LIMIT:
        # All exceptions survive in the addressed full result; counters signal
        # that an omitted list is not evidence of success.
        keys = ('ok', 'decision', 'error', 'activity', 'delivery', 'check_counts', 'review_counts',
                'attention', 'retry_blocked', 'experience', 'handoff_path', 'quality_review', 'next_action', 'revision_instruction')
        if kind == 'plan':
            p = value.get('project') or {}
            value = {'project': {k: p.get(k) for k in ('id', 'status', 'summary', 'next_action', 'quality_status', 'attention', 'method_recovery', 'presentation')}}
        else:
            value = {k: value[k] for k in keys if k in value}
            if 'quality_review' in value:
                value['quality_review'].pop('criteria', None)
        value.update(details_path=reference['path'], details_sha256=reference['sha256'],
                     details_required=True, instruction='Leggi il risultato completo prima di decidere; le liste omesse non sono controlli superati.')
    # A malicious/oversize input must not turn into an unbounded control message.
    if len(json.dumps(value, ensure_ascii=False)) > LIMIT:
        value = {k: value.get(k) for k in ('ok', 'decision', 'check_counts', 'review_counts', 'details_path', 'details_sha256')}
        value['details_required'] = True
    return json.dumps(value, ensure_ascii=False)

"""Read-only version labels and review targets, independent of specialist titles."""
from pathlib import Path


def number_attempts(project):
    """Persist monotonically increasing numbers, including failed/in-progress work."""
    attempts = [a for step in project['steps'] for a in step['attempts']
                if (a.get('context') or {}).get('purpose') == 'delivery'
                or (a.get('context') or {}).get('purpose', 'work') not in ('preview', 'review')
                and project.get('product_path') and project['product_path'] in a.get('output_files', [])]
    attempts.sort(key=lambda a: (a.get('started_at', ''), a.get('finished_at', '')))
    counter = max([project.get('version_counter', 0), *[a.get('version_number', 0) for a in attempts]])
    changed = False
    for attempt in attempts:
        if not attempt.get('version_number'):
            counter += 1
            attempt['version_number'] = counter
            changed = True
    if changed:
        project['version_counter'] = counter
    return changed


def annotate(deliveries, project, workspace, artifact):
    attempts = [(step, attempt) for step in project['steps'] for attempt in step['attempts']]
    attempts.sort(key=lambda item: (item[1].get('started_at', ''), item[1].get('finished_at', ''), item[0]['id']))
    by_id = {d['id']: d for d in deliveries}
    targets = {}
    for step, attempt in attempts:
        identifier = (attempt.get('delivery_record') or {}).get('id') or Path(attempt.get('output_dir', '')).name or step['id']
        purpose = (attempt.get('context') or {}).get('purpose', 'work')
        current = bool(project.get('product_path') and project['product_path'] in attempt.get('output_files', []))
        category = ('review' if purpose == 'review' or attempt.get('quality_review') else 'sample' if purpose == 'preview'
                    else 'version' if purpose == 'delivery' or current else 'contribution')
        delivery = by_id.get(identifier)
        if delivery is None:
            continue
        delivery.update(category=category, version=attempt.get('version_number') if category == 'version' else None,
                        execution_status=attempt.get('status', ''), file_count=len(attempt.get('output_files', [])),
                        role_title=attempt.get('role_title', ''))
        for filename in attempt.get('output_files', []):
            path = artifact(workspace, filename)
            if path:
                targets[str(path)] = delivery
    for step, attempt in attempts:
        review = attempt.get('quality_review')
        if not review:
            continue
        identifier = (attempt.get('delivery_record') or {}).get('id') or Path(attempt.get('output_dir', '')).name or step['id']
        delivery = by_id.get(identifier)
        if not delivery:
            continue
        target = artifact(workspace, review.get('product_path', ''))
        parent = targets.get(str(target)) if target else None
        delivery['review'] = {'target_delivery_id': parent['id'] if parent else None,
            'target_version': parent.get('version') if parent else None,
            'target_label': parent['title'] if parent else 'Risultato precedente non presente nell’elenco',
            'status': review.get('status', 'needs_review'), 'validated': bool(attempt.get('validated')),
            'matches_current_brief': not project.get('acceptance') or review.get('contract_hash') == project['acceptance']['hash'],
            'report_path': review.get('report_path', ''), 'correction_count': len(review.get('revision_actions', []))}
    return deliveries

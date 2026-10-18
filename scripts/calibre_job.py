#!/usr/bin/env python3
"""Trusted helper run by the pinned calibre-debug Python runtime, never model code."""
import json
import os
from pathlib import Path
import sys


def main():
    import calibre
    # The pinned checker uses detect_ncpus for both CSS pages and parser threads.
    calibre._ncpus = max(1, min(8, int(os.environ.get('ARTCRAFT_CPU_THREADS', '2'))))
    from calibre.ebooks.oeb.polish.container import get_container
    action, book, output = sys.argv[1:]
    container = get_container(book)
    opf = container.opf
    def values(name):
        return [str(v) for v in opf.xpath('//*[local-name()="' + name + '"]/text()')]
    value = {'path': book, 'format': Path(book).suffix[1:].upper(),
             'title': values('title'), 'authors': values('creator'), 'languages': values('language'),
             'spine': [{'file': name, 'linear': linear} for name, linear in container.spine_names],
             'resources': len(container.mime_map), 'files': sorted(container.mime_map)}
    if action == 'check':
        from calibre.ebooks.oeb.polish.check.main import run_checks
        from calibre.ebooks.oeb.polish.check.base import WARN
        issues = run_checks(container)
        value['issues'] = [{'rule': e.rule_id, 'severity': 'error' if e.level > WARN else 'warning',
                            'file': e.name, 'line': e.line, 'message': str(e)} for e in issues]
        value['status'] = 'failed' if any(e.level > WARN for e in issues) or not value['spine'] else 'passed'
        value['note'] = 'Controllo strutturale nativo Calibre; non prova qualità editoriale, resa su lettori o conformità EPUBCheck.'
    Path(output).write_text(json.dumps(value, ensure_ascii=False, indent=2))
    close = getattr(container, 'close', None)
    if close:
        close()


if __name__ == '__main__':
    main()

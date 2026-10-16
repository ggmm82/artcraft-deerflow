#!/usr/bin/env python3
"""Browser acceptance of the real progress component with declared API fixtures.

No account, LLM or production data. Install the pinned UI test dependencies from
the workflow and pass their node_modules directory. The component is bundled
directly from frontend/, with only the shared HTTP/base-URL adapters stubbed.
"""
import argparse
from datetime import datetime, timedelta, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import tempfile
import threading

from playwright.sync_api import sync_playwright, expect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node-modules', type=Path, required=True)
    args = parser.parse_args()
    modules = args.node_modules.resolve()
    root = Path(__file__).resolve().parents[1]
    now = datetime.now(timezone.utc)
    iso = lambda time: time.isoformat()
    job = {'job_id': 'artcraft-job-123456abcdef', 'agent': 'cadcraft', 'engine': 'codex',
           'model': 'fixture-model', 'phase': 'running_tool', 'summary': 'Comando CadCraft in esecuzione',
           'work_summary': 'Creo il modello modificabile e controllo le dimensioni',
           'created_at': iso(now - timedelta(minutes=18)), 'started_at': iso(now - timedelta(minutes=18)),
           'finished_at': '', 'deadline_at': iso(now + timedelta(minutes=7)),
           'last_activity_at': iso(now - timedelta(minutes=3)), 'heartbeat_at': iso(now),
           'files': [{'name': 'robot-source.json', 'size': 120}], 'files_count': 1,
           'events': [{'at': iso(now - timedelta(minutes=18)), 'phase': 'planning',
                       'summary': 'Creo il modello modificabile e controllo le dimensioni'}]}
    project = {'id': 'fixture-project', 'brief': 'Robot che balla', 'steps': [
        {'id': 'visual', 'agent': 'photocraft', 'goal': 'Preparo immagini e texture',
         'status': 'completed', 'depends_on': [], 'attempts': []},
        {'id': 'motion', 'agent': 'effectcraft', 'goal': 'Animo il robot con gli asset dei colleghi',
         'status': 'running', 'depends_on': ['visual'], 'attempts': []},
        {'id': 'audio', 'agent': 'soundcraft', 'goal': 'Preparo la base ritmica',
         'status': 'pending', 'depends_on': ['motion'], 'attempts': []},
        {'id': 'final', 'agent': 'filmcraft', 'goal': 'Monto animazione e audio',
         'status': 'pending', 'depends_on': ['motion', 'audio'], 'attempts': []}]}
    state = {'job': job, 'unavailable': False, 'project': project}
    with tempfile.TemporaryDirectory(prefix='progress-ui-') as directory:
        folder = Path(directory)
        (folder / 'fetch.ts').write_text('export const fetch = (...args: Parameters<typeof globalThis.fetch>) => globalThis.fetch(...args);')
        (folder / 'config.ts').write_text('export const getBackendBaseURL = () => "";')
        component = json.dumps(str(root / 'frontend/delegate-progress.tsx'))
        (folder / 'entry.tsx').write_text('''import React from 'react';
import { createRoot } from 'react-dom/client';
import { DelegateProgress } from ''' + component + ''';
const root=createRoot(document.getElementById('root')!);
window.showThread=(threadId='fixture',active=true,pending=true)=>root.render(<DelegateProgress threadId={threadId} active={active} pending={pending}/>);
window.showThread();
''')
        subprocess.run([str(modules / '.bin/esbuild'), str(folder / 'entry.tsx'), '--bundle', '--jsx=automatic',
                        '--outfile=' + str(folder / 'app.js'),
                        '--alias:react=' + str(modules / 'react'), '--alias:react-dom=' + str(modules / 'react-dom'),
                        '--alias:@/core/api/fetcher=' + str(folder / 'fetch.ts'),
                        '--alias:@/core/config=' + str(folder / 'config.ts')], check=True, capture_output=True)
        (folder / 'index.html').write_text('<!doctype html><meta charset="utf-8"><div id="root"></div><script src="/app.js"></script>')

        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path.endswith('/studio-jobs'):
                    self.send_response(503 if state['unavailable'] else 200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    jobs = [state['job']] if '/fixture/' in self.path else []
                    self.wfile.write(json.dumps({'jobs': jobs,
                        'project': state['project'] if '/fixture/' in self.path else None}).encode())
                else:
                    super().do_GET()

        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=directory))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
                page = browser.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{server.server_port}')
                card = page.get_by_test_id('delegate-job')
                plan = page.get_by_test_id('team-plan')
                expect(plan.get_by_text('1 di 4 fasi verificate', exact=False)).to_be_visible()
                for name in ('Photocraft', 'Effectcraft', 'Soundcraft', 'Filmcraft'):
                    expect(plan.get_by_text(name, exact=True)).to_be_visible()
                expect(plan.get_by_text('Riceve da: Effectcraft, Soundcraft')).to_be_visible()
                expect(plan.get_by_text('Il limite di 25 minuti', exact=False)).to_be_visible()
                expect(card.get_by_text('18 min', exact=False).first).to_be_visible()
                expect(card.get_by_text('Nessun nuovo avanzamento', exact=False)).to_be_visible()
                expect(card.get_by_text('Worker raggiungibile')).to_be_visible()
                expect(card.get_by_text('Non è una stima di consegna.', exact=False)).to_be_visible()
                expect(card.get_by_text('robot-source.json', exact=False)).to_be_visible()
                expect(card.get_by_text(job['work_summary']).first).to_be_visible()
                state['job'] = {**job, 'phase': 'exporting', 'summary': 'Esportazione del modello e dell’anteprima',
                                'last_activity_at': iso(datetime.now(timezone.utc)),
                                'heartbeat_at': iso(datetime.now(timezone.utc))}
                expect(card.get_by_test_id('delegate-summary')).to_have_text(state['job']['summary'], timeout=6000)
                page.reload()
                expect(plan.get_by_text('Robot che balla', exact=True)).to_be_visible()
                expect(card.get_by_test_id('delegate-summary')).to_have_text(state['job']['summary'])
                expect(card.get_by_text('18 min', exact=False).first).to_be_visible()
                state['job'] = {**state['job'], 'heartbeat_at': iso(now - timedelta(minutes=2))}
                expect(card.get_by_text('Segnale del worker assente', exact=False)).to_be_visible(timeout=6000)
                state['unavailable'] = True
                expect(page.get_by_text('Aggiornamenti non disponibili:', exact=False)).to_be_visible(timeout=6000)
                expect(card.get_by_test_id('delegate-summary')).to_have_text(state['job']['summary'])
                state['unavailable'] = False
                state['job'] = {**state['job'], 'phase': 'completed', 'summary': 'Consegna verificata',
                                'finished_at': iso(datetime.now(timezone.utc))}
                state['project']['steps'][1]['status'] = 'needs_revision'
                expect(plan.get_by_text('Da riprendere o correggere', exact=False)).to_be_visible(timeout=6000)
                expect(card.get_by_test_id('delegate-summary')).to_have_text('Consegna verificata', timeout=6000)
                expect(card.get_by_text('Segnale del worker assente', exact=False)).not_to_be_visible()
                page.evaluate("window.showThread('another-conversation',false,false)")
                expect(page.get_by_test_id('delegate-job')).to_have_count(0)
                expect(page.get_by_test_id('team-plan')).to_have_count(0)
                page.evaluate("window.showThread('fixture',false,false)")
                expect(page.get_by_test_id('delegate-summary')).to_have_text('Consegna verificata')
                assert not errors, errors
                browser.close()
            print('Browser OK: team plan, dependencies, partial recovery, live updates, 18-minute clock, lost heartbeat, network retry, reload and conversation isolation.')
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    main()

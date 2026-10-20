#!/usr/bin/env python3
"""Real React+Tailwind browser acceptance: dock, previews, recovery and isolation.

Uses declared API fixtures and tiny genuine media, without accounts or an LLM.
The chat/composer layout mirrors the pinned upstream flex layout; integration
placement is checked separately against both real upstream pages.
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
    repo = Path(__file__).resolve().parents[1]
    now = datetime.now(timezone.utc)
    iso = lambda t: t.isoformat()
    video_path = '/mnt/user-data/outputs/filmcraft/preview.mp4'
    job = {'job_id': 'artcraft-job-123456abcdef', 'agent': 'effectcraft', 'engine': 'codex',
        'model': 'fixture-model', 'phase': 'running_tool', 'summary': 'Esporto il risultato con Effectcraft',
        'resources': {'memory_bytes': 1073741824, 'memory_limit_bytes': 2147483648, 'oom_kills': 0},
        'limits': {'cpus': 1.5}, 'operations': [{'id': 'render', 'state': 'running', 'label': 'Render finale', 'elapsed_seconds': 600, 'progress': {'done': 12, 'total': 48}}],
        'work_summary': 'Correggo inquadratura e proporzioni del robot prima del render',
        'created_at': iso(now - timedelta(minutes=18)), 'started_at': iso(now - timedelta(minutes=18)),
        'finished_at': '', 'deadline_at': iso(now + timedelta(minutes=7)),
        'last_activity_at': iso(now - timedelta(minutes=3)), 'heartbeat_at': iso(now),
        'files': [{'name': 'robot.ecproj', 'size': 120}], 'files_count': 1,
        'events': [{'at': iso(now - timedelta(minutes=18)), 'phase': 'planning', 'summary': 'Esporto il risultato con Effectcraft'}]}
    project = {'id': 'fixture-project', 'brief': 'Robot che balla', 'status': 'working',
        'outcome': {'title': 'Progetto dimostrativo', 'result': 'Video completo da presentare', 'format': 'MP4 e progetto modificabile', 'use': 'Presentazione', 'quality': 'Versione curata', 'constraints': [], 'assumptions': [], 'questions': []},
        'strategy': {'state': 'exploring', 'method': 'Composizione alternativa', 'reason': 'Il primo campione non rispetta i vincoli',
            'user_action': '', 'stop_reason': '', 'alternatives': [{'method': 'Costruzione da riferimenti', 'reason': 'Verificare prima gli elementi essenziali',
            'status': 'tested', 'tools': ['vectorcraft'], 'evidence': [{'path': '/mnt/user-data/outputs/review/report.json', 'sha256': 'fixture'}]}]},
        'method_recovery': {'message': 'Il metodo va rivalutato prima di richiedere risorse esterne'},
        'summary': 'Preparo una prima versione completa', 'next_action': 'Integro immagine, movimento e audio',
        'product_path': video_path, 'quality_status': 'not_reviewed',
        'acceptance': {'user_requests': ['Conserva il contenuto del riferimento fornito'],
            'request_documents': [{'path': '/mnt/user-data/.studio-project/requests/original.txt'}],
            'request_manifest': {'path': '/mnt/user-data/.studio-project/requests/index.json'}, 'request_count': 12, 'criteria': [
            {'id': 'request_fidelity', 'requirement': 'Contenuto conforme alla richiesta originale', 'critical': True}]},
        'review_criteria': [{'requirement_id': 'request_fidelity', 'criterion': 'Conformità', 'method': 'content',
            'status': 'failed', 'evidence': 'Il contenuto è stato sostituito con una variante non richiesta.'}],
        'revision_actions': [{'requirement_id': 'request_fidelity', 'action': 'Correggere il contenuto usando il riferimento originale',
            'strategy': 'change_method', 'priority': 1}],
        'comparison': {'baseline_path': '/mnt/user-data/outputs/previous.txt', 'criteria': [
            {'requirement_id': 'request_fidelity', 'status': 'unchanged', 'evidence': 'Il difetto osservato è ancora presente'}]},
        'deliveries': [{'id': 'final', 'title': 'Robot con musica — versione 2', 'agent': 'filmcraft', 'at': iso(now),
                       'current': True, 'technical_status': 'needs_revision', 'issues': ['Texture collegata mancante'], 'purpose': 'delivery'},
                      {'id': 'old', 'title': 'Prima prova muta', 'agent': 'effectcraft', 'at': iso(now-timedelta(hours=1)),
                       'current': False, 'technical_status': 'not_verified', 'issues': [], 'purpose': 'preview'}],
        'results': [{'path': video_path, 'label': 'preview.mp4', 'agent': 'filmcraft', 'validated': True, 'at': iso(now),
                     'delivery_id': 'final', 'role': 'export'},
                    {'path': '/mnt/user-data/outputs/filmcraft/Sorgenti.zip', 'label': 'Sorgenti.zip', 'agent': 'filmcraft', 'validated': True, 'at': iso(now),
                     'delivery_id': 'final', 'role': 'source_archive', 'open_with': 'Estrarre tutto, preparare i percorsi e aprire montaggio.locale.fcproj',
                     'editability': 'Timeline e clip separate'},
                    {'path': '/mnt/user-data/outputs/effectcraft/bozza.mp4', 'label': 'bozza.mp4', 'agent': 'effectcraft', 'validated': True, 'at': iso(now-timedelta(hours=1)),
                     'delivery_id': 'old', 'role': 'export'}],
        'steps': [{'id': 'visual', 'agent': 'photocraft', 'goal': 'Preparo immagini e texture', 'status': 'completed'},
                  {'id': 'motion', 'agent': 'effectcraft', 'goal': 'Animo il robot', 'status': 'running'},
                  {'id': 'audio', 'agent': 'soundcraft', 'goal': 'Verifico il mix recuperato', 'status': 'paused'},
                  {'id': 'final', 'agent': 'filmcraft', 'goal': 'Monto una prova con audio', 'status': 'pending'}]}
    state = {'job': job, 'project': project, 'unavailable': False}
    with tempfile.TemporaryDirectory(prefix='adaptive-studio-ui-') as directory:
        folder = Path(directory)
        (folder / 'fetch.ts').write_text('export const fetch = (...args: Parameters<typeof globalThis.fetch>) => globalThis.fetch(...args);')
        (folder / 'config.ts').write_text('export const getBackendBaseURL = () => "";')
        (folder / 'entry.tsx').write_text('''import React from 'react';
import {createRoot} from 'react-dom/client';
import {DelegateProgress} from ''' + json.dumps(str(repo / 'frontend/delegate-progress.tsx')) + ''';
const root=createRoot(document.getElementById('root')!);
window.continued=0; window.failContinue=false;
window.showThread=(threadId='fixture',active=true,pending=true,error=false)=>root.render(<DelegateProgress threadId={threadId} active={active} pending={pending} coordinatorError={error} onContinue={()=>{window.continued++;if(window.failContinue)return Promise.reject(new Error("fixture submit unavailable"))}}/>);
window.showThread();
''')
        subprocess.run([str(modules / '.bin/esbuild'), str(folder / 'entry.tsx'), '--bundle', '--jsx=automatic',
            '--outfile=' + str(folder / 'app.js'), '--alias:react=' + str(modules / 'react'),
            '--alias:react-dom=' + str(modules / 'react-dom'), '--alias:@/core/api/fetcher=' + str(folder / 'fetch.ts'),
            '--alias:@/core/config=' + str(folder / 'config.ts')], check=True, capture_output=True)
        paragraphs = ''.join('<p class="mb-10">Messaggio storico %d: dettagli di una conversazione lunga.</p>' % i for i in range(100))
        (folder / 'index.html').write_text('''<!doctype html><html><meta name="viewport" content="width=device-width, initial-scale=1"><meta charset="utf-8"><link rel="stylesheet" href="/app.css">
<body><main class="mx-auto flex h-dvh max-w-[960px] flex-col"><header class="shrink-0 border-b p-3">Chat ArtCraft</header><div id="messages" class="min-h-0 flex-1 overflow-y-auto p-3">'''+paragraphs+'''</div><footer class="shrink-0 p-3"><div id="root"></div><textarea class="h-14 w-full rounded border p-2" aria-label="Scrivi un messaggio"></textarea></footer></main><script src="/app.js"></script></body></html>''')
        css = '@import ' + json.dumps(str(modules / 'tailwindcss/index.css')) + ' source(none);\n'
        css += '@source ' + json.dumps(str(repo / 'frontend/delegate-progress.tsx')) + ';\n@source "./index.html";\n'
        css += '@layer base { * { border-color: var(--color-border); } }\n'
        css += '@theme { --color-background: #ffffff; --color-foreground: #0f172a; --color-muted: #f1f5f9; --color-border: #cbd5e1; --color-ring: #2563eb; --color-muted-foreground: #64748b; }\n'
        (folder / 'input.css').write_text(css)
        subprocess.run([str(modules / '.bin/tailwindcss'), '-i', str(folder / 'input.css'), '-o', str(folder / 'app.css')],
                       check=True, capture_output=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=160x90:rate=10',
            '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000', '-t', '1', '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(folder / 'preview.mp4')], check=True, capture_output=True)

        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                valid = self.path == '/api/threads/fixture/studio-delivery/accept' and data.get('delivery_id') == 'final'
                if valid:
                    state['project'] = {**state['project'], 'status': 'ready', 'quality_status': 'accepted_by_user'}
                self.send_response(200 if valid else 409)
                self.send_header('Content-Type', 'application/json'); self.end_headers()
                self.wfile.write(json.dumps({'project': state['project']}).encode())

            def do_PUT(self):
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', '0'))))
                state['experience_excluded'] = body['excluded']
                self.do_GET()

            def do_GET(self):
                if '/studio-experience' in self.path:
                    self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers()
                    self.wfile.write(json.dumps({'total':1,'excluded':int(state.get('experience_excluded',False)), 'observations':[{
                        'id':'a'*64,'at':'2026-10-20T00:00:00Z','excluded':state.get('experience_excluded',False),
                        'observation':{'criterion':'Risorse portabili','status':'failed','method':'functional','evidence':'Risorsa collegata mancante',
                        'corrections':['Includere tutte le risorse'],'tools':{'filmcraft':'fixture'},'product_sha256':'b'*64,'report_sha256':'c'*64}}]}).encode()); return
                if self.path.endswith('/studio-jobs'):
                    self.send_response(503 if state['unavailable'] else 200)
                    self.send_header('Content-Type', 'application/json'); self.end_headers()
                    owned = '/fixture/' in self.path
                    try:
                        reported_job = {**state['job'], 'heartbeat_at': iso(datetime.now(timezone.utc))}
                        self.wfile.write(json.dumps({'jobs': [reported_job] if owned else [],
                            'project': state['project'] if owned else None}).encode())
                    except (BrokenPipeError, ConnectionResetError):
                        pass  # Navigation deliberately aborts the previous request.
                elif '/artifacts/' in self.path:
                    self.send_response(200); self.send_header('Content-Type', 'video/mp4'); self.end_headers()
                    self.wfile.write((folder / 'preview.mp4').read_bytes())
                else:
                    super().do_GET()

        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=directory))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width': 1100, 'height': 800})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{server.server_port}')
                dock = page.get_by_test_id('delegate-progress')
                expect(page.get_by_test_id('studio-status')).to_have_text('Avanzamento da verificare')
                expect(page.get_by_test_id('studio-summary')).to_have_text('Render finale · 12/48 campioni')
                expect(page.get_by_test_id('studio-health')).to_contain_text('Nessun nuovo avanzamento')
                expect(page.get_by_test_id('delegate-job')).to_have_count(0)  # no wall of technical detail
                composer = page.get_by_role('textbox', name='Scrivi un messaggio')
                for viewport in ({'width': 1100, 'height': 800}, {'width': 390, 'height': 740}):
                    page.set_viewport_size(viewport)
                    for offset in (0, 20000):
                        page.locator('#messages').evaluate('(el, offset)=>el.scrollTop=offset', offset)
                        box, input_box = dock.bounding_box(), composer.bounding_box()
                        assert box['y'] >= 0 and box['y'] + box['height'] <= input_box['y'] + 1
                        assert input_box['y'] + input_box['height'] <= viewport['height']
                    page.get_by_role('button', name='Vedi risultato', exact=True).click()
                    expect(page.get_by_text('Bozza di lavoro:', exact=False)).to_be_visible()
                    page.wait_for_function('document.querySelector("[data-testid=studio-drawer]").getBoundingClientRect().top >= 0')
                    drawer = page.get_by_test_id('studio-drawer').bounding_box()
                    assert drawer['y'] + drawer['height'] <= dock.bounding_box()['y']
                    expect(page.get_by_role('button', name='Chiudi dettagli del progetto')).to_be_in_viewport()
                    composer.evaluate('(el)=>el.style.height="140px"')
                    page.wait_for_function('document.querySelector("[data-testid=studio-drawer]").getBoundingClientRect().top >= 0')
                    expect(page.get_by_role('button', name='Chiudi dettagli del progetto')).to_be_in_viewport()
                    composer.evaluate('(el)=>el.style.height=""')
                    expect(page.get_by_test_id('paired-sources').get_by_role('link', name='Sorgenti.zip')).to_be_visible()
                    expect(page.get_by_test_id('paired-sources').get_by_role('link', name='bozza.mp4')).to_have_count(0)
                    assert page.get_by_test_id('primary-result').evaluate('(el)=>!!(el.compareDocumentPosition(document.querySelector("[data-testid=acceptance-criteria]")) & Node.DOCUMENT_POSITION_FOLLOWING)')
                    video = page.get_by_label('Anteprima video')
                    video.evaluate('(v)=>v.play()')
                    page.wait_for_function('document.querySelector("video").currentTime > .1')
                    video.evaluate('(v)=>v.pause()')
                    page.get_by_test_id('studio-drawer-content').evaluate('(el)=>el.scrollTop=el.scrollHeight')
                    expect(page.get_by_role('button', name='Chiudi dettagli del progetto')).to_be_in_viewport()
                    page.get_by_role('button', name='Chiudi dettagli del progetto').click()
                page.get_by_role('button', name='Esperienza', exact=True).click()
                experience_panel = page.get_by_test_id('experience-panel')
                expect(experience_panel).to_contain_text('1 osservazioni conservate')
                expect(experience_panel).to_contain_text('Risorsa collegata mancante')
                page.get_by_role('button', name='Escludi dal riutilizzo', exact=True).click()
                expect(page.get_by_role('button', name='Riattiva il riutilizzo')).to_be_visible()
                page.get_by_role('button', name='Chiudi dettagli del progetto').click()
                page.get_by_role('button', name='Attività', exact=True).click()
                expect(page.get_by_test_id('operation-progress')).to_contain_text('12/48 campioni osservati')
                expect(page.get_by_text('RAM worker: 1024 MiB / 2048 MiB · 1.5 CPU')).to_be_visible()
                page.get_by_role('button', name='Chiudi dettagli del progetto').click()
                # A professional role is compiled from the project, independently of CLI names.
                state['job'] = {**job, 'role_id': 'coherence', 'role_title': 'Responsabile della coerenza', 'role_version': 'abcdef0123456789'}
                state['project'] = {**project, 'roles': [{'id': 'coherence', 'title': 'Responsabile della coerenza',
                    'mission': 'Confrontare risultati e vincoli', 'expertise': ['Analisi delle dipendenze'],
                    'checks': ['Confrontare il risultato con il brief integrale'], 'tools': [], 'version': 'abcdef0123456789'},
                    {'id': 'verify', 'title': 'Revisore indipendente', 'mission': 'Verificare la consegna', 'expertise': ['Verifiche indipendenti'], 'checks': ['Raccogliere evidenze'], 'tools': [], 'version': 'fedcba0123456789'}],
                    'steps': [{**step, 'role_id': 'coherence' if step['id'] == 'motion' else 'verify' if step['id'] == 'final' else '', 'attempt_count': 1 if step['id'] == 'motion' else 0} for step in project['steps']]}
                page.reload()
                expect(page.get_by_test_id('studio-status')).to_have_text('Avanzamento da verificare')
                page.get_by_role('button', name='Squadra', exact=True).click()
                compiled = page.get_by_test_id('compiled-role').first
                expect(compiled).to_contain_text('Al lavoro')
                expect(compiled).to_contain_text('Analisi delle dipendenze')
                expect(page.get_by_test_id('compiled-role').nth(1)).to_contain_text('Previsto')
                compiled.locator('summary').click()
                expect(compiled).to_contain_text('Strumenti di base del progetto')
                expect(compiled).to_contain_text('Confrontare il risultato con il brief integrale')
                expect(compiled).to_contain_text('Versione abcdef012345')
                state['job'] = job
                page.get_by_role('button', name='Progetto', exact=True).click()
                overview = page.get_by_test_id('project-overview')
                expect(overview).to_contain_text('Video completo da presentare')
                expect(overview).to_contain_text('MP4 e progetto modificabile')
                expect(overview).to_contain_text('1 di 4 incarichi conclusi')
                expect(overview).to_contain_text('Traguardo in corso:')
                expect(page.get_by_test_id('project-method')).to_contain_text('Composizione alternativa')
                expect(page.get_by_test_id('project-method')).to_contain_text('Prova disponibile')
                expect(page.get_by_test_id('project-method')).to_contain_text('prima di richiedere risorse esterne')
                expect(page.get_by_test_id('project-method').get_by_role('link', name='Prova 1')).to_have_attribute('href', '/api/threads/fixture/artifacts/mnt/user-data/outputs/review/report.json')
                expect(page.get_by_test_id('revision-actions')).to_contain_text('Correggere il contenuto usando il riferimento originale')
                expect(page.get_by_test_id('revision-actions')).to_contain_text('Serve provare un metodo diverso')
                expect(page.get_by_test_id('quality-comparison')).to_contain_text('Invariato')
                expect(page.get_by_test_id('quality-comparison')).to_contain_text('Il difetto osservato è ancora presente')
                expect(page.get_by_test_id('project-identity')).to_contain_text('Progetto dimostrativo')
                # A change of live roles must not mix old context into today's remaining work.
                state['project'] = {**state['project'], 'orientation': {'active_step_ids': ['motion', 'final'],
                    'history_step_ids': ['visual', 'audio'], 'history_count': 2},
                    'steps': [{**step, 'role_id': 'retired' if step['id'] in ('visual', 'audio') else step.get('role_id', '')} for step in state['project']['steps']]}
                page.reload()
                page.get_by_role('button', name='Progetto', exact=True).click()
                expect(page.get_by_test_id('project-position')).to_contain_text('0 di 2 incarichi conclusi')
                expect(page.get_by_test_id('project-history')).to_contain_text('Altre attività del progetto (2)')
                page.get_by_test_id('project-history').locator('summary').click()
                expect(page.get_by_test_id('project-history')).to_contain_text('Verifico il mix recuperato')
                page.get_by_role('button', name='Squadra', exact=True).click()
                expect(page.get_by_test_id('team-plan')).not_to_contain_text('Verifico il mix recuperato')
                state['project'] = {**project, 'status': 'clarifying', 'outcome': {**project['outcome'], 'format': '', 'questions': ['Una proposta di lavoro o un prodotto pronto da distribuire?']}}
                state['job'] = {**job, 'phase': 'completed', 'finished_at': iso(now)}
                page.reload()
                page.evaluate("window.showThread('fixture',false,false,false)")
                expect(page.get_by_test_id('studio-status')).to_have_text('Definiamo il risultato insieme')
                expect(page.get_by_role('button', name='Riprendi lavoro')).to_have_count(0)
                page.get_by_role('button', name='Progetto', exact=True).click()
                expect(page.get_by_test_id('brief-questions')).to_contain_text('Una proposta di lavoro o un prodotto pronto da distribuire?')
                expect(page.get_by_test_id('project-overview')).to_contain_text('Da definire con te')
                state['job'] = job
                page.evaluate("window.showThread('fixture',true,true,false)")
                # A report-only inventory must never replace the selected artifact.
                state['project'] = {**project, 'results': [{'path': '/mnt/user-data/outputs/review/report.json',
                    'label': 'report.json', 'agent': 'filmcraft', 'validated': True, 'at': iso(now)}]}
                page.reload()
                page.get_by_role('button', name='Vedi risultato', exact=True).click()
                expect(page.get_by_label('Anteprima video')).to_have_attribute('src', '/api/threads/fixture/artifacts'+video_path)
                page.get_by_test_id('acceptance-criteria').locator('summary').click()
                expect(page.get_by_test_id('acceptance-criteria')).to_contain_text('Conserva il contenuto del riferimento fornito')
                expect(page.get_by_test_id('acceptance-criteria')).to_contain_text('Da correggere')
                expect(page.get_by_role('link', name='Leggi la richiesta originale completa')).to_have_attribute('href',
                    '/api/threads/fixture/artifacts/mnt/user-data/.studio-project/requests/original.txt?download=true')
                # Document/project outputs use the same result control, not a video-only flow.
                state['project'] = {**state['project'], 'product_path': '/mnt/user-data/outputs/report/final.docx'}
                page.reload()
                page.get_by_role('button', name='Vedi risultato', exact=True).click()
                expect(page.get_by_role('link', name='final.docx')).to_be_visible()
                expect(page.get_by_label('Anteprima video')).to_have_count(0)
                # A document without product_path is still discoverable, and old media cannot replace it.
                document = {'path': '/mnt/user-data/outputs/software/release.zip', 'label': 'release.zip',
                            'agent': 'workspace', 'validated': True, 'at': iso(now), 'delivery_id': 'final', 'role': 'export',
                            'open_with': 'Estrarre il pacchetto e seguire README'}
                state['project'] = {**project, 'product_path': '', 'results': [document, project['results'][2]]}
                page.reload()
                page.get_by_role('button', name='Vedi risultato', exact=True).click()
                expect(page.get_by_test_id('primary-result').get_by_role('link', name='release.zip')).to_be_visible()
                expect(page.get_by_test_id('primary-result')).to_contain_text('Estrarre il pacchetto')
                expect(page.get_by_label('Anteprima video')).to_have_count(0)
                expect(page.get_by_test_id('paired-sources')).to_have_count(0)
                state['project'] = project
                page.reload()
                page.get_by_role('button', name='Squadra', exact=True).click()
                for name in ('Photocraft', 'Effectcraft', 'Soundcraft', 'Filmcraft'):
                    expect(page.get_by_test_id('team-plan').get_by_text(name, exact=True)).to_be_visible()
                page.get_by_role('button', name='File e sorgenti', exact=False).click()
                groups = page.get_by_test_id('delivery-group')
                expect(groups).to_have_count(2)
                expect(groups.first).to_contain_text('Consegna incompleta')
                expect(groups.first.get_by_role('link', name='Sorgenti.zip')).to_be_visible()
                expect(groups.first).to_contain_text('montaggio.locale.fcproj')
                expect(groups.first.get_by_role('link', name='bozza.mp4')).to_have_count(0)
                expect(groups.nth(1).get_by_role('link', name='bozza.mp4')).not_to_be_visible()
                groups.nth(1).locator('summary').first.click()
                expect(groups.nth(1).get_by_role('link', name='bozza.mp4')).to_be_visible()
                page.get_by_role('button', name='Attività', exact=True).click()
                card = page.get_by_test_id('delegate-job')
                expect(card.get_by_text('18 min', exact=False).first).to_be_visible()
                expect(card.get_by_text('Non è una stima di consegna.', exact=False)).to_be_visible()
                page.reload()
                expect(page.get_by_test_id('studio-summary')).to_have_text('Render finale · 12/48 campioni')
                expect(page.get_by_test_id('studio-drawer')).to_have_count(0)
                state['job'] = {**job, 'phase': 'failed', 'summary': 'Quota esaurita', 'finished_at': iso(now)}
                state['project'] = {**project, 'status': 'blocked', 'attention': {
                    'code': 'provider_quota', 'message': 'Il servizio AI ha esaurito la quota: i file salvati restano disponibili.',
                    'action': 'Scegli un servizio disponibile oppure attendi il ripristino.'}}
                page.evaluate("window.showThread('fixture',false,false,true)")
                expect(page.get_by_test_id('studio-status')).to_have_text('Il lavoro è in pausa', timeout=7000)
                expect(page.get_by_role('link', name='Apri La tua squadra')).to_be_visible()
                page.evaluate('window.failContinue=true')
                page.get_by_role('button', name='Riprendi lavoro').click()
                expect(page.get_by_role('alert')).to_contain_text('Non riesco a inviare')
                expect(page.get_by_role('button', name='Riprendi lavoro')).to_be_enabled()
                page.evaluate('window.failContinue=false')
                page.get_by_role('button', name='Riprendi lavoro').click()
                assert page.evaluate('window.continued') == 2
                expect(page.get_by_role('button', name='Ripresa richiesta…')).to_be_disabled()
                expect(page.get_by_role('button', name='Vedi risultato', exact=True)).to_be_enabled()
                state['unavailable'] = True
                expect(page.get_by_text('Aggiornamenti non disponibili:', exact=False)).to_be_visible(timeout=7000)
                expect(page.get_by_role('button', name='Vedi risultato', exact=True)).to_be_enabled()
                state['unavailable'] = False
                state['project'] = {**project, 'status': 'ready', 'product_path': video_path, 'quality_status': 'passed',
                    'deliveries': [{**d, 'technical_status': 'passed', 'issues': []} for d in project['deliveries']]}
                page.evaluate("window.showThread('fixture',false,false,false)")
                expect(page.get_by_test_id('studio-status')).to_have_text('Il risultato è pronto', timeout=7000)
                expect(page.get_by_role('button', name='Riprendi lavoro')).to_have_count(0)
                page.get_by_role('button', name='Vedi risultato', exact=True).click()
                expect(page.get_by_text('Prodotto finale', exact=True)).to_be_visible()
                page.evaluate("window.showThread('another-conversation',false,false,false)")
                expect(dock).to_have_count(0)
                page.evaluate("window.showThread('fixture',false,false,false)")
                expect(page.get_by_test_id('studio-status')).to_have_text('Il risultato è pronto')
                state['project'] = {**state['project'], 'status': 'review', 'quality_status': 'needs_review'}
                expect(page.get_by_test_id('studio-status')).to_have_text('Una versione è disponibile', timeout=7000)
                expect(page.get_by_role('button', name='Riprendi lavoro')).to_have_count(0)
                page.get_by_role('button', name='Vedi risultato', exact=True).click()
                page.get_by_role('button', name='Ho verificato: accetta questa versione').click()
                expect(page.get_by_test_id('studio-status')).to_have_text('Il risultato è pronto')
                expect(page.get_by_text('Questa versione è stata accettata da te.')).to_be_visible()
                assert not errors, errors
                browser.close()
            print('Browser OK: real Tailwind dock visible beside composer on desktop/mobile during chat scrolling; playable preview; adaptive team; 18-minute clock; quota pause; continue action; network recovery; reload and conversation isolation.')
        finally:
            server.shutdown(); server.server_close()


if __name__ == '__main__':
    main()

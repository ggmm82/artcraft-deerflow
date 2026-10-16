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
        'work_summary': 'Correggo inquadratura e proporzioni del robot prima del render',
        'created_at': iso(now - timedelta(minutes=18)), 'started_at': iso(now - timedelta(minutes=18)),
        'finished_at': '', 'deadline_at': iso(now + timedelta(minutes=7)),
        'last_activity_at': iso(now - timedelta(minutes=3)), 'heartbeat_at': iso(now),
        'files': [{'name': 'robot.ecproj', 'size': 120}], 'files_count': 1,
        'events': [{'at': iso(now - timedelta(minutes=18)), 'phase': 'planning', 'summary': 'Esporto il risultato con Effectcraft'}]}
    project = {'id': 'fixture-project', 'brief': 'Robot che balla', 'status': 'working',
        'summary': 'Preparo una prima versione completa', 'next_action': 'Integro immagine, movimento e audio',
        'results': [{'path': video_path, 'label': 'preview.mp4', 'agent': 'filmcraft', 'validated': True, 'at': iso(now)}],
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
        css += '@theme { --color-background: #ffffff; --color-muted-foreground: #64748b; }\n'
        (folder / 'input.css').write_text(css)
        subprocess.run([str(modules / '.bin/tailwindcss'), '-i', str(folder / 'input.css'), '-o', str(folder / 'app.css')],
                       check=True, capture_output=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=160x90:rate=10',
            '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000', '-t', '1', '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(folder / 'preview.mp4')], check=True, capture_output=True)

        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path.endswith('/studio-jobs'):
                    self.send_response(503 if state['unavailable'] else 200)
                    self.send_header('Content-Type', 'application/json'); self.end_headers()
                    owned = '/fixture/' in self.path
                    try:
                        self.wfile.write(json.dumps({'jobs': [state['job']] if owned else [],
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
                expect(page.get_by_test_id('studio-status')).to_have_text('Effectcraft sta lavorando')
                expect(page.get_by_test_id('studio-summary')).to_have_text(job['summary'])
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
                    video = page.get_by_label('Anteprima video')
                    video.evaluate('(v)=>v.play()')
                    page.wait_for_function('document.querySelector("video").currentTime > .1')
                    video.evaluate('(v)=>v.pause()')
                    page.get_by_role('button', name='Chiudi dettagli del progetto').click()
                page.get_by_role('button', name='Squadra', exact=True).click()
                for name in ('Photocraft', 'Effectcraft', 'Soundcraft', 'Filmcraft'):
                    expect(page.get_by_test_id('team-plan').get_by_text(name, exact=True)).to_be_visible()
                page.get_by_role('button', name='Attività', exact=True).click()
                card = page.get_by_test_id('delegate-job')
                expect(card.get_by_text('18 min', exact=False).first).to_be_visible()
                expect(card.get_by_text('Non è una stima di consegna.', exact=False)).to_be_visible()
                page.reload()
                expect(page.get_by_test_id('studio-summary')).to_have_text(job['summary'])
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
                state['project'] = {**project, 'status': 'ready', 'product_path': video_path}
                page.evaluate("window.showThread('fixture',false,false,false)")
                expect(page.get_by_test_id('studio-status')).to_have_text('Il risultato è pronto', timeout=7000)
                expect(page.get_by_role('button', name='Riprendi lavoro')).to_have_count(0)
                page.get_by_role('button', name='Vedi risultato', exact=True).click()
                expect(page.get_by_text('Prodotto finale', exact=True)).to_be_visible()
                page.evaluate("window.showThread('another-conversation',false,false,false)")
                expect(dock).to_have_count(0)
                page.evaluate("window.showThread('fixture',false,false,false)")
                expect(page.get_by_test_id('studio-status')).to_have_text('Il risultato è pronto')
                assert not errors, errors
                browser.close()
            print('Browser OK: real Tailwind dock visible beside composer on desktop/mobile during chat scrolling; playable preview; adaptive team; 18-minute clock; quota pause; continue action; network recovery; reload and conversation isolation.')
        finally:
            server.shutdown(); server.server_close()


if __name__ == '__main__':
    main()

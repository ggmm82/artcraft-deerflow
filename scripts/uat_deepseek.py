#!/usr/bin/env python3
"""Opt-in browser acceptance test against an isolated ArtCraft deployment.

Credentials are environment variables. No HAR, trace, request bodies or keys
are recorded. --thread-url verifies and downloads an already completed test.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import zipfile

from playwright.sync_api import expect, sync_playwright
from pypdf import PdfReader

PROMPT = ('Collaudo utente: usa studio_delegate con gridcraft per analizzare il CSV allegato '
    'e produrre vendite.xlsx con importi numerici 10,20,30, formula di somma con totale 60 '
    'e riepilogo.json verificato. Poi passa il riepilogo a wordcraft con studio_delegate '
    'e crea relazione.docx e relazione.pdf in italiano con il totale 60. '
    'Esegui gli incarichi in sequenza, richiedi handoff.json a entrambi e consegna i tre file '
    'con present_files. Mantieni il lavoro essenziale, senza chiarimenti né perfezionamenti facoltativi.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:2026')
    parser.add_argument('--output', type=Path, default=Path('reports/uat-browser'))
    parser.add_argument('--initialize-admin', action='store_true')
    parser.add_argument('--thread-url', help='Riapre una conversazione completata e prova i download senza nuove chiamate LLM')
    parser.add_argument('--timeout', type=int, default=1800)
    args = parser.parse_args()
    args.base_url = args.base_url.rstrip('/')
    if args.thread_url and urlsplit(args.thread_url).netloc != urlsplit(args.base_url).netloc:
        parser.error('--thread-url deve appartenere all’istanza di collaudo')
    required = ['UAT_EMAIL', 'UAT_PASSWORD'] + ([] if args.thread_url else ['DEEPSEEK_API_KEY'])
    if any(not os.getenv(name) for name in required):
        parser.error('Impostare ' + ', '.join(required) + ' nell’ambiente')
    args.output.mkdir(parents=True, exist_ok=True)
    report = {'base_url': args.base_url, 'cases': [], 'network': [], 'downloads': []}
    def passed(name):
        report['cases'].append({'name': name, 'status': 'passed'})
        print('PASS:', name, flush=True)
    def snapshot(page, name):
        page.screenshot(path=str(args.output / (name + '.png')), full_page=True, timeout=20000)
    def save_report():
        (args.output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    try:
        with tempfile.TemporaryDirectory(prefix='artcraft-uat-browser-') as profile, sync_playwright() as p:
            options = {'headless': True, 'viewport': {'width': 1440, 'height': 1100}, 'accept_downloads': True}
            if os.getenv('UAT_HTTP_PASSWORD'):
                options['http_credentials'] = {'username': os.getenv('UAT_HTTP_USER', 'admin'),
                                               'password': os.environ['UAT_HTTP_PASSWORD']}
            context = p.chromium.launch_persistent_context(profile, **options)
            page = context.new_page()
            page.on('response', lambda response: report['network'].append({
                'path': urlsplit(response.url).path, 'status': response.status,
                'method': response.request.method}) if '/api/' in response.url else None)
            page.goto(args.base_url + '/workspace/chats/new', wait_until='domcontentloaded')
            page.locator('input[type=email], textarea').first.wait_for(timeout=30000)
            if page.locator('input[type=email]').count():
                page.locator('input[type=email]').fill(os.environ['UAT_EMAIL'])
                page.locator('input[type=password]').first.fill(os.environ['UAT_PASSWORD'])
                if page.locator('#confirmPassword').count():
                    if not args.initialize_admin:
                        raise ValueError('Istanza non inizializzata: usare --initialize-admin solo sul proprio ambiente di prova')
                    page.locator('#confirmPassword').fill(os.environ['UAT_PASSWORD'])
                    page.get_by_role('button', name='Create Admin Account', exact=True).click()
                else:
                    page.get_by_role('button', name='Sign In', exact=True).click()
                page.wait_for_url('**/workspace**', timeout=30000)
            passed('Accesso utente dal browser')
            if not args.thread_url:
                page.goto(args.base_url + '/workspace/studio', wait_until='domcontentloaded')
                frame = page.frame_locator('iframe[title="ArtCraft Studio"]')
                expect(frame.locator('#deepseek-state')).to_have_text(re.compile(r'^(Chiave configurata|Da collegare)$'), timeout=30000)
                before = frame.locator('#deepseek-state').inner_text(timeout=30000)
                frame.locator('#deepseek-key').fill('invalid-uat-key')
                frame.locator('#deepseek-connect').click()
                expect(frame.locator('#status')).to_have_text('Chiave DeepSeek rifiutata', timeout=40000)
                expect(frame.locator('#deepseek-state')).to_have_text(before)
                passed('Chiave errata rifiutata senza cambiare la connessione')
                frame.locator('#deepseek-key').fill(os.environ['DEEPSEEK_API_KEY'])
                frame.locator('#deepseek-connect').click()
                expect(frame.locator('#deepseek-state')).to_have_text('Chiave configurata', timeout=40000)
                expect(frame.locator('#deepseek-key')).to_have_value('')
                passed('Chiave reale collegata e campo segreto svuotato')
                for app in ['GridCraft', 'WordCraft']:
                    card = frame.locator('section.box').filter(has=frame.get_by_role('heading', name=app, exact=True))
                    card.get_by_role('combobox', name='Motore ' + app).select_option('deepseek')
                    card.get_by_role('button', name='Salva', exact=True).click()
                    expect(frame.locator('#status')).to_have_text(app + ': configurazione salvata')
                page.reload(wait_until='domcontentloaded')
                frame = page.frame_locator('iframe[title="ArtCraft Studio"]')
                for app in ['GridCraft', 'WordCraft']:
                    expect(frame.get_by_role('combobox', name='Motore ' + app)).to_have_value('deepseek', timeout=15000)
                passed('Scelta specialisti persistente dopo ricaricamento')
                snapshot(page, '01-deepseek-connected')
                page.get_by_role('link', name='New chat', exact=True).click()
                page.locator('textarea').wait_for(timeout=30000)
                if not page.get_by_role('button', name='Studio · DeepSeek', exact=True).count():
                    page.get_by_role('button', name='Studio · Codex', exact=True).click()
                    page.get_by_role('button', name='Studio · DeepSeek (studio-deepseek)', exact=True).click()
                passed('Selezione del coordinatore DeepSeek')
                sample = args.output / 'vendite-collaudo.csv'
                sample.write_text('Voce,Importo\nA,10\nB,20\nC,30\n')
                page.locator('input[type=file]').first.set_input_files(str(sample.resolve()))
                page.locator('textarea').fill(PROMPT)
                snapshot(page, '02-request')
                page.get_by_role('button', name='Submit', exact=True).click()
                page.wait_for_url(re.compile(r'/chats/(?!new)[^/]+$'), timeout=30000)
                passed('Caricamento CSV e invio richiesta')
                thread = page.url.rsplit('/', 1)[-1]
                deadline = time.monotonic() + args.timeout
                while time.monotonic() < deadline:
                    page.wait_for_timeout(2000)
                    # Passive observation only: the chat request is sent by the UI.
                    response = context.request.get(args.base_url + '/api/threads/' + thread + '/runs')
                    if response.ok:
                        runs = response.json()
                        if runs and runs[0]['status'] not in ('pending', 'running'):
                            report['run_status'] = runs[0]['status']
                            if runs[0]['status'] != 'success':
                                raise RuntimeError('Conversazione terminata con stato ' + runs[0]['status'])
                            break
                else:
                    raise TimeoutError('Timeout del collaudo utente')
                passed('Conversazione completata dal prodotto')
            else:
                page.goto(args.thread_url, wait_until='domcontentloaded')
            report['thread_url'] = page.url
            archive = page.get_by_role('button', name='Download current versions (3 files)', exact=True)
            expect(archive).to_be_visible(timeout=30000)
            snapshot(page, '03-delivered')
            with page.expect_download(timeout=60000) as pending:
                archive.click()
            download = pending.value
            downloaded = args.output / Path(download.suggested_filename).name
            download.save_as(downloaded)
            report['downloads'].append({'filename': downloaded.name, 'bytes': downloaded.stat().st_size})
            extracted = {}
            with zipfile.ZipFile(downloaded) as bundle:
                for suffix in ('.xlsx', '.docx', '.pdf'):
                    matches = [name for name in bundle.namelist() if name.endswith(suffix)]
                    if len(matches) != 1:
                        raise ValueError('Archivio senza un unico file ' + suffix)
                    content = bundle.read(matches[0])
                    extracted[suffix] = args.output / Path(matches[0]).name
                    extracted[suffix].write_bytes(content)
            passed('Download archivio con XLSX, DOCX e PDF dalla chat')
            link = page.locator('a[href*="/artifacts/"][href*=".xlsx"][href*="download=true"]').first
            with page.expect_download(timeout=30000) as pending:
                link.click()
            download = pending.value
            download.save_as(args.output / ('individual-' + Path(download.suggested_filename).name))
            passed('Download individuale XLSX')
            ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            numbers, formula_totals = [], []
            with zipfile.ZipFile(extracted['.xlsx']) as workbook:
                if workbook.testzip() is not None:
                    raise ValueError('XLSX corrotto')
                for name in workbook.namelist():
                    if re.fullmatch(r'xl/worksheets/sheet\d+\.xml', name):
                        sheet = ET.fromstring(workbook.read(name))
                        for cell in sheet.findall('.//s:c', ns):
                            if cell.get('t') not in ('s', 'str', 'inlineStr'):
                                try:
                                    value = float(cell.findtext('s:v', namespaces=ns))
                                    numbers.append(value)
                                    formula = cell.findtext('s:f', namespaces=ns) or ''
                                    if 'SUM(' in formula.upper():
                                        formula_totals.append(value)
                                except (TypeError, ValueError):
                                    pass
            if not all(value in numbers for value in (10, 20, 30)) or 60 not in formula_totals:
                raise ValueError('XLSX senza dati numerici o formula con totale 60')
            passed('XLSX: importi numerici e formula con valore salvato 60')
            with zipfile.ZipFile(extracted['.docx']) as document:
                if document.testzip() is not None:
                    raise ValueError('DOCX corrotto')
                tree = ET.fromstring(document.read('word/document.xml'))
                docx_text = ' '.join(node.text or '' for node in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
            pdf = PdfReader(extracted['.pdf'])
            pdf_text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
            if not re.search(r'(?<!\d)60(?!\d)', docx_text) or not re.search(r'(?<!\d)60(?!\d)', pdf_text):
                raise ValueError('Totale 60 non trovato in DOCX/PDF')
            report['independent_checks'] = {'xlsx_numeric_values': [10, 20, 30],
                'xlsx_formula_cached_total': 60, 'pdf_pages': len(pdf.pages),
                'docx_contains_total': True, 'pdf_contains_total': True}
            passed('DOCX e PDF leggibili con totale 60')
            (args.output / 'conversation.txt').write_text(page.locator('body').inner_text())
            report['passed'] = True
            context.close()
    except Exception as error:
        message = str(error)
        for name in ('DEEPSEEK_API_KEY', 'UAT_PASSWORD', 'UAT_HTTP_PASSWORD'):
            if os.getenv(name):
                message = message.replace(os.environ[name], '[REDACTED]')
        report.update(passed=False, error=message)
        print('FAIL:', message, flush=True)
    finally:
        save_report()
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

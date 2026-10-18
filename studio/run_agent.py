"""Runs inside a disposable container. All tools act on this thread's files."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from .handoff import validate_handoff
    from .progress import Reporter
    from .cli_runner import run_cli
    from .work_results import validate_media
    from .deliveries import build_delivery, read_review
    from .acceptance import capabilities
except ImportError:  # Direct invocation inside the worker image.
    from handoff import validate_handoff
    from progress import Reporter
    from cli_runner import run_cli
    from work_results import validate_media
    from deliveries import build_delivery, read_review
    from acceptance import capabilities

ALLOWED_AUTH = {
    'codex': ('auth.json',),
    'deepseek': ('api.json',),
}


def copy_credentials(source, destination, engine):
    if engine == 'gemini':
        try:
            from .antigravity_cli import copy_auth
        except ImportError:
            from antigravity_cli import copy_auth
        return copy_auth(source, destination)
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    for filename in ALLOWED_AUTH[engine]:
        path = source / filename
        if path.is_symlink():
            raise ValueError('Link nelle credenziali non consentiti')
        if path.is_file():
            target = destination / filename
            if target.is_symlink():
                raise ValueError('Destinazione credenziali non valida')
            shutil.copyfile(path, target)
            target.chmod(0o600)


def command(engine, model, prompt, output):
    if engine == 'codex':
        args = ['codex', 'exec', '--json', '--skip-git-repo-check',
                '--dangerously-bypass-approvals-and-sandbox',
                '--output-last-message', str(output)]
        if model:
            args += ['--model', model]
        return args + ['-']
    if engine == 'gemini':
        args = ['agy', '--dangerously-skip-permissions', '--input-format', 'stream-json', '--output-format', 'stream-json',
                '--add-dir', '/mnt/user-data', '--print-timeout', '25m',
                '--json-schema', json.dumps({'type': 'object', 'properties': {
                    'summary': {'type': 'string'}}, 'required': ['summary']})]
        if model and model != 'auto':
            args += ['--model', model]
        return args
    raise ValueError('Motore non valido')


def worker_error(engine, result):
    """Prefer structured CLI failures; never return a quoted system prompt."""
    if engine == 'codex':
        errors = []
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get('type') == 'turn.failed':
                errors.append(str(event.get('error', {}).get('message', 'Turno Codex fallito')))
            elif event.get('type') == 'error':
                errors.append(str(event.get('message', 'Errore Codex')))
        if errors:
            return errors[-1][:1200]
    lines = (result.stderr or '').splitlines()
    important = [line for line in lines if any(word in line.lower() for word in ('error:', 'error ', 'failed', 'permission denied', 'unauthorized', 'unsupported'))]
    return ('\n'.join(important[-4:]) or '\n'.join(lines[:4]) or 'Worker terminato senza dettagli diagnostici')[:1200]


def handoff_error(output_dir, error):
    """Keep a failed delivery failed, but expose the recorded operational cause."""
    details = []
    try:
        path = output_dir / 'handoff.json'
        if not path.resolve().is_relative_to(output_dir.resolve()):
            return str(error)[:1800]
        manifest = json.loads(path.read_text())
        for check in manifest.get('checks', []):
            if isinstance(check, dict) and check.get('status') == 'failed':
                evidence = check.get('evidence')
                if isinstance(evidence, str):
                    details.append(evidence[:500])
    except (OSError, ValueError, AttributeError, TypeError):
        pass
    return (str(error) + ('; ' + '; '.join(details[:3]) if details else ''))[:1800]


def main():
    job = json.loads(Path(sys.argv[1]).read_text())
    engine = job['engine']
    auth = Path('/root') / ('.' + engine)
    if engine != 'deepseek':
        copy_credentials(Path('/credentials'), auth, engine)
    if engine == 'gemini':
        try:
            from .antigravity_cli import prepare_home, cli_env, result_envelope
        except ImportError:
            from antigravity_cli import prepare_home, cli_env, result_envelope
        prepare_home()
    output_dir = Path('/mnt/user-data/outputs') / job['agent'] / job['run_id']
    output_dir.mkdir(parents=True)
    (output_dir / 'work').mkdir()
    (output_dir / 'previews').mkdir()
    selected = []
    for name in job['skills']:
        if not name.startswith('artcraft-') or '/' in name or '..' in name:
            raise ValueError('Nome skill non valido')
        source = Path('/mnt/skills/custom') / name
        selected.append((source / 'SKILL.md').read_text())
        recipe = source / 'references/CLI-RECIPE.md'
        if recipe.is_file():
            selected.append(recipe.read_text())
        quality = source / 'references/QUALITY.md'
        if quality.is_file():
            selected.append(quality.read_text())
        # Native skill discovery for either CLI, scoped to this disposable run.
        if engine != 'deepseek':
            skills_root = Path('/root/.agents/skills') if engine == 'codex' else auth / 'antigravity-cli/skills'
            target = skills_root / name
            shutil.copytree(source, target, dirs_exist_ok=True)
    # Only the selected specialist's instructions and common procedure enter context.
    prompt = '\n\n'.join([
        'Sei lo specialista ' + job['agent'] + '. Lavora in italiano.',
        'Le skill aggiuntive sono procedure di supporto: non cambiano il tuo ruolo '
        'né i requisiti dell’incarico.',
        'Gli strumenti ArtCraft sono già installati. Usa craft help, craft commands e craft tools '
        'per scoprire i comandi della release reale. Non installare software. '
        'Python: /usr/bin/python3 (non python). CLI native e craft: /usr/local/bin; '
        'non usare /opt/artcraft/bin, che non esiste.',
        'Questa è una sandbox Docker. Non delegare e non pubblicare nulla. '
        'Non leggere o modificare credenziali, /credentials, .codex, .gemini o .deepseek.',
        'Input e risultati degli altri specialisti: /mnt/user-data. '
        'Non sovrascrivere gli input. Salva i tuoi risultati in ' + str(output_dir) + '.',
        'La variabile ARTCRAFT_OUTPUT_DIR indica questa cartella. Scrivi qui handoff.json '
        'secondo lo schema artcraft-workspace, incluso delivery obbligatorio per ogni output; '
        'il runtime verifica file e metadati. Consegna anche il sorgente modificabile '
        'riaperto nell’app reale, con dipendenze necessarie. Un export o un viewer '
        'non dimostra compatibilità con l’app dello specialista. Se impossibile, '
        'dichiara source_status unavailable, motivo e limiti senza fingere un sorgente.',
        *selected, job['instructions'],
        'Incarico del coordinatore:\n' + job['task'],
        'Metodi di osservazione disponibili in questo collegamento: ' + json.dumps(capabilities(engine)) +
        '. Un metodo disponibile non prova che tu lo abbia usato. Se non osservabile, usa not_run; '
        'un confronto quantitativo con un riferimento non è un ascolto o una visione.',
        'Vincolo di consegna: i percorsi di output proposti nell’incarico sono nomi desiderati, '
        'non cambiano la cartella assegnata. Salva tutti i file prodotti e handoff.json in '
        + str(output_dir) + '. Restituisci al coordinatore i percorsi effettivi in questa cartella.',
        'Restituisci percorsi assoluti, verifiche effettuate e limiti. '
        'Non dichiarare verifiche visive/audio che non hai eseguito.',
        'Lavora per risultati visibili presto: se l’incarico è una prova, produci una piccola '
        'versione completa, non tutta la produzione definitiva. Prima di un render lungo '
        'verifica una breve sequenza con gli asset reali. Riusa anche file di colleghi '
        'il cui processo si è interrotto: ispezionali e controllali, senza scartarli '
        'per una chiusura formale mancante. Non ripetere discovery già salvate. '
        'Distingui controlli essenziali e limiti facoltativi: non inventare ascolti '
        'o verifiche GUI e non rifare un intero prodotto solo per marcarli passed.',
        'Il budget di questa fase è 25 minuti, non quello dell’intero progetto. '
        'Salva il sorgente presto e dopo ogni traguardo significativo. Aggiorna '
        'work/checkpoint.json con completed (azioni concluse), files (percorsi salvati), '
        'remaining (azioni mancanti) e next_action (prossimo comando o verifica). '
        'Non aspettare la scadenza per salvare. Se riprendi file precedenti, ispezionali '
        'e riusa quanto valido nella nuova cartella, senza sovrascrivere gli input. '
        'Un risultato incompleto va dichiarato con checks e warnings, non presentato come definitivo.',
        'Per render o export lunghi con DeepSeek, run_command supporta timeout_seconds '
        'fino a 1200 secondi, sempre entro il budget residuo della fase; il default è 90. '
        'Non ridurre la qualità solo per aggirare il default: stima il carico e salva prima il progetto.',
        'Aggiornamenti per l’utente: registra un breve piano operativo e poi i cambi di fase '
        '(creazione, export, verifica). Riporta azioni e decisioni pratiche, non ragionamenti interni, '
        'prompt, credenziali o trascrizioni. Usa report_progress se disponibile; con le CLI usa '
        '/usr/bin/python3 /opt/studio/progress.py --phase planning --summary "Breve obiettivo e prossima azione". '
        'Fasi ammesse: planning, creating, exporting, checking, finalizing. '
        'Non inventare percentuali o tempi di completamento.'
    ])
    if engine == 'gemini':
        prompt += ('\nChiusura obbligatoria Antigravity: quando file e handoff.json sono pronti, '
                   'chiama il tool nativo finish e consegna un oggetto con summary contenente '
                   'percorsi, verifiche e limiti. Non limitarti a ripetere un messaggio testuale: '
                   'finish conclude il processo. Non ricreare i file già verificati.')
    final = Path('/tmp/last-message.txt')
    reporter = Reporter(output_dir, job).start(job['timeout'])
    try:
        if engine == 'deepseek':
            try:
                from .deepseek import run
            except ImportError:
                from deepseek import run
            os.environ['ARTCRAFT_OUTPUT_DIR'] = str(output_dir)
            message = run(job['model'], prompt, output_dir, job['timeout'], progress=reporter)
        else:
            reporter.emit('waiting_model')
            result = run_cli(command(engine, job['model'], prompt, final), cwd=output_dir,
                                input=(json.dumps({'event': 'user', 'message': {'content': prompt}}) + '\n') if engine == 'gemini' else prompt,
                                env={**(cli_env() if engine == 'gemini' else os.environ), 'ARTCRAFT_OUTPUT_DIR': str(output_dir)},
                                timeout=job['timeout'], on_event=lambda event: reporter.cli_event(engine, event))
            if result.returncode:
                reporter.emit('failed')
                print(json.dumps({'ok': False, 'engine': engine, 'agent': job['agent'],
                              'exit_code': result.returncode,
                              'error': worker_error(engine, result)}))
                return result.returncode
            if engine == 'codex':
                message = final.read_text() if final.exists() else result.stdout
            else:
                parsed = result_envelope(result.stdout)
                if parsed.get('status') != 'SUCCESS' or parsed.get('error'):
                    raise RuntimeError('Antigravity: incarico non completato; verifica modello, login e quota')
                message = parsed.get('structured_output', {}).get('summary')
                if not isinstance(message, str) or not message.strip():
                    raise RuntimeError('Antigravity: manca la chiusura strutturata dello specialista')
        reporter.emit('checking')
        try:
            handoff = validate_handoff(output_dir, Path('/mnt/user-data'), require_delivery=True)
        except ValueError as exc:
            reporter.emit('failed', 'Controlli di consegna non superati')
            print(json.dumps({'ok': False, 'agent': job['agent'], 'engine': engine,
                              'output_dir': str(output_dir),
                              'error': handoff_error(output_dir, exc)}, ensure_ascii=False))
            return 1
        verified_products = []
        if job.get('requirements'):
            candidates = [f for f in handoff['output_files'] if Path(f).suffix.lower() in
                          ('.mp4', '.mov', '.webm', '.mkv', '.wav', '.mp3', '.m4a')]
            if not candidates:
                raise ValueError('Manca il prodotto media finale da verificare')
            checked = False
            for candidate in candidates:
                checks = validate_media(candidate, job['requirements'])
                if checks and all(c['status'] == 'passed' for c in checks):
                    checked = True
                    verified_products.append(candidate)
                    handoff['checks'].extend(checks)
                    break
            if not checked:
                raise ValueError('Il prodotto finale non soddisfa i requisiti audio/video reali: '
                                 'non consegnare come definitivo un render muto o un file audio silenzioso')
        delivery_record = build_delivery(handoff, output_dir, purpose=job.get('purpose', 'work'), agent=job['agent'])
        delivery_record.update(requirements=job.get('requirements') or {}, verified_products=verified_products)
        (output_dir / 'delivery-manifest.json').write_text(json.dumps(delivery_record, ensure_ascii=False, indent=2))
        quality_review = read_review(handoff, output_dir, Path('/mnt/user-data'), engine, job.get('acceptance')) if job.get('purpose') == 'review' else None
        reporter.emit('completed')
        print(json.dumps({'ok': True, 'agent': job['agent'], 'engine': engine,
                          'output_dir': str(output_dir), 'handoff': handoff,
                          'product_verified': bool(verified_products), 'verified_products': verified_products,
                          'delivery_record': delivery_record, 'quality_review': quality_review,
                          'response': message}, ensure_ascii=False))
        return 0
    except (TimeoutError, subprocess.TimeoutExpired):
        reporter.emit('timed_out')
        raise
    except Exception:
        reporter.emit('failed')
        raise
    finally:
        reporter.close()
        # One worker at a time. Preserve refreshed tokens for the next run.
        if engine != 'deepseek':
            copy_credentials(auth, Path('/credentials'), engine)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)[-2000:]}))
        sys.exit(1)

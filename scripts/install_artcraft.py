#!/usr/bin/env python3
"""Scarica le release fissate e verifica SHA-256 prima di installarle."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import tarfile
import tempfile
import time
import urllib.request


def safe_extract(archive, destination):
    """Nessun file speciale o percorso esterno; conserva link relativi interni."""
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            name = Path(member.name)
            if name.is_absolute() or '..' in name.parts:
                raise ValueError(f'Percorso archivio non valido: {member.name}')
            target = destination / name
            if not target.resolve().is_relative_to(destination):
                raise ValueError(f'Percorso esterno: {member.name}')
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, target.open('wb') as output:
                    shutil.copyfileobj(source, output)
                target.chmod(member.mode & 0o777)
            elif member.issym():
                if Path(member.linkname).is_absolute():
                    raise ValueError(f'Link assoluto: {member.name}')
                if not (target.parent / member.linkname).resolve().is_relative_to(destination):
                    raise ValueError(f'Link esterno: {member.name}')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(member.linkname)
            elif member.islnk():
                source = (destination / member.linkname).resolve()
                if not source.is_relative_to(destination) or not source.is_file():
                    raise ValueError(f'Hard link non valido: {member.name}')
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            else:
                raise ValueError(f'File speciale non consentito: {member.name}')


def download(asset, output):
    for attempt in range(3):
        try:
            digest = hashlib.sha256()
            request = urllib.request.Request(asset['url'], headers={'User-Agent': 'artcraft-deerflow-config/1'})
            with urllib.request.urlopen(request, timeout=120) as source, output.open('wb') as dest:
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
                    dest.write(chunk)
            if digest.hexdigest() != asset['sha256']:
                raise ValueError(f'Checksum SHA-256 errato: {asset["name"]}')
            if output.stat().st_size != asset['size_bytes']:
                raise ValueError(f'Dimensione errata: {asset["name"]}')
            return
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arch', default='')
    parser.add_argument('--root', type=Path, default=Path('/opt/artcraft'))
    parser.add_argument('--bin-dir', type=Path, default=Path('/usr/local/bin'))
    args = parser.parse_args()
    arch = args.arch or {'x86_64': 'amd64', 'aarch64': 'arm64'}.get(platform.machine())
    if arch not in ('amd64', 'arm64'):
        parser.error('Architetture supportate: amd64 e arm64')
    lock = json.loads((args.root / 'versions.lock.json').read_text())
    installed = []
    args.bin_dir.mkdir(parents=True, exist_ok=True)
    for app in lock['applications']:
        asset = app['assets'][arch]
        print(f'Installazione {app["id"]} {app["version"]} ({arch})', flush=True)
        destination = args.root / 'apps' / app['id']
        with tempfile.TemporaryDirectory(prefix='artcraft-install-') as temp:
            archive = Path(temp) / asset['name']
            download(asset, archive)
            safe_extract(archive, destination)
        matches = [p for p in destination.rglob(app['executable']) if p.is_file()]
        if len(matches) != 1:
            raise RuntimeError(f'Atteso un eseguibile {app["executable"]}, trovati {matches}')
        binary = matches[0].resolve()
        binary.chmod(binary.stat().st_mode | 0o111)
        link = args.bin_dir / app['executable']
        if link.exists() or link.is_symlink():
            raise RuntimeError(f'Non sovrascrivo un eseguibile esistente: {link}')
        link.symlink_to(binary)
        installed.append({'id': app['id'], 'version': app['version'], 'binary': str(binary), 'sha256': asset['sha256']})
    (args.root / 'installed.json').write_text(json.dumps(installed, indent=2) + '\n')
    print(f'Installate {len(installed)} CLI.', flush=True)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Scarica le release fissate e verifica SHA-256 prima di installarle."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import zipfile


def safe_unzip(archive, destination):
    """EPUBCheck distribution: reject traversal, symlinks and excessive expansion."""
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as zipped:
        if sum(item.file_size for item in zipped.infolist()) > 512 * 1024 * 1024:
            raise ValueError('ZIP distribution too large')
        for item in zipped.infolist():
            name = Path(item.filename)
            target = destination / name
            if (name.is_absolute() or '..' in name.parts or '\\' in item.filename
                    or stat.S_ISLNK(item.external_attr >> 16) or not target.resolve().is_relative_to(destination)):
                raise ValueError('Unsafe ZIP member: ' + item.filename)
            if item.is_dir(): target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zipped.open(item) as source, target.open('wb') as output:
                    shutil.copyfileobj(source, output)


def install_deb(asset, archive):
    """Primary .deb is hashed; dependencies use authenticated Debian repositories."""
    archive.chmod(0o644)
    subprocess.run(['apt-get', 'update'], check=True)
    subprocess.run(['apt-get', 'install', '-y', '--no-install-recommends', str(archive)], check=True,
                   env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})
    version = subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', asset['package']], text=True)
    if version != asset['package_version']:
        raise RuntimeError('Installed Debian version differs from lock: ' + asset['package'])


def install_toolkit(app, archive, destination, root, bin_dir, arch):
    kind = app['install']['kind']
    destination.mkdir(parents=True, exist_ok=True)
    if kind == 'debian':
        install_deb(app['assets'][arch], archive)
        return app['install']['native_path']
    if kind == 'zip':
        safe_unzip(archive, destination)
        return str(next(destination.rglob('epubcheck.jar')))
    if kind == 'npm':
        target = root / 'toolkit'
        target.mkdir(parents=True, exist_ok=True)
        for name in ('package.json', 'package-lock.json'):
            shutil.copy2(root / 'toolkit-lock' / name, target / name)
        subprocess.run(['npm', 'ci', '--prefix', str(target), '--ignore-scripts', '--omit=optional', '--no-audit', '--no-fund'], check=True)
        version = json.loads((target / 'node_modules/@playwright/test/package.json').read_text())['version']
        if version != app['version']: raise RuntimeError('NPM version differs from application lock')
        subprocess.run(['node', str(target / 'node_modules/playwright/cli.js'), 'install', 'chromium', '--only-shell'], check=True,
                       env={**os.environ, 'PLAYWRIGHT_BROWSERS_PATH': str(root / 'playwright-browsers')})
        subprocess.run(['npm', 'cache', 'clean', '--force'], check=True)
        return str(target / 'node_modules/playwright/cli.js')
    if kind == 'freecad-appimage':
        # Extract the verified official image: no FUSE/mount privilege required.
        archive.chmod(0o755)
        subprocess.run([str(archive), '--appimage-extract'], cwd=destination, check=True,
                       stdout=subprocess.DEVNULL)
        binary = destination / 'squashfs-root/usr/bin/python'
        if not binary.is_file():
            raise RuntimeError('Official FreeCAD image has no bundled Python')
        return str(binary)
    if kind in ('fluidsynth-cmake', 'ffmpeg-source'):
        safe_extract(archive, destination)
        source = destination / app['install']['source_dir']
        prefix = destination / 'runtime'
        if kind == 'fluidsynth-cmake':
            build = destination / 'build'
            subprocess.run(['cmake', '-S', str(source), '-B', str(build),
                            '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_INSTALL_PREFIX=' + str(prefix),
                            '-DBUILD_SHARED_LIBS=OFF', '-Denable-readline=OFF',
                            '-Denable-pulseaudio=OFF', '-Denable-alsa=OFF', '-Denable-jack=OFF',
                            '-Denable-portaudio=OFF', '-Denable-dbus=OFF', '-Denable-ladspa=OFF',
                            '-Denable-network=OFF', '-Denable-libsndfile=ON'], check=True)
            subprocess.run(['cmake', '--build', str(build), '--parallel', '2'], check=True)
            subprocess.run(['cmake', '--install', str(build)], check=True)
            names = ['fluidsynth']
            shutil.rmtree(build)
        else:
            subprocess.run([str(source / 'configure'), '--prefix=' + str(prefix),
                            '--disable-debug', '--disable-doc', '--disable-shared', '--enable-static',
                            '--enable-gpl', '--enable-libx264', '--enable-libx265', '--enable-libvpx',
                            '--enable-libopus', '--enable-libmp3lame', '--enable-libvorbis',
                            '--enable-libass', '--enable-libfontconfig', '--enable-libfreetype',
                            '--enable-libharfbuzz'], cwd=source, check=True)
            subprocess.run(['make', '-j2'], cwd=source, check=True)
            subprocess.run(['make', 'install'], cwd=source, check=True)
            names = ['ffmpeg', 'ffprobe']
        for name in names:
            binary = prefix / 'bin' / name
            if not binary.is_file(): raise RuntimeError('Missing built executable: ' + name)
            (bin_dir / name).symlink_to(binary)
        shutil.rmtree(source)
        return str(prefix / 'bin' / names[0])
    if kind == 'whisper-cmake':
        safe_extract(archive, destination)
        source = destination / app['install']['source_dir']
        build = destination / 'build'
        subprocess.run(['cmake', '-S', str(source), '-B', str(build), '-DCMAKE_BUILD_TYPE=Release',
                        '-DGGML_NATIVE=OFF', '-DGGML_CUDA=OFF', '-DWHISPER_BUILD_TESTS=OFF',
                        '-DBUILD_SHARED_LIBS=OFF'], check=True)
        subprocess.run(['cmake', '--build', str(build), '--config', 'Release', '--target', 'whisper-cli', '--parallel', '2'], check=True)
        binary = build / 'bin/whisper-cli'
        (bin_dir / 'whisper-cli').symlink_to(binary)
        # The public-domain JFK speech is kept only as an offline native fixture.
        shutil.copy2(source / 'samples/jfk.wav', destination / 'jfk.wav')
        return str(binary)
    raise ValueError('Unsupported installation kind: ' + kind)


def safe_extract(archive, destination):
    """Nessun file speciale o percorso esterno; conserva link relativi interni."""
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, 'r:*') as tar:
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


def install_binaries(app, destination, bin_dir):
    executable = app.get('binary', app['executable'])
    binary = None
    for name, relative in app.get('binary_paths', {executable: None}).items():
        if Path(name).name != name or name in ('', '.', '..'):
            raise ValueError('Nome eseguibile non valido')
        matches = [destination / relative] if relative is not None else [p for p in destination.rglob(name) if p.is_file()]
        if (len(matches) != 1 or not matches[0].is_file()
                or not matches[0].resolve().is_relative_to(destination.resolve())):
            raise RuntimeError(f'Atteso un eseguibile interno {name}, trovati {matches}')
        target = matches[0].resolve()
        target.chmod(target.stat().st_mode | 0o111)
        link = bin_dir / name
        if link.exists() or link.is_symlink():
            raise RuntimeError(f'Non sovrascrivo un eseguibile esistente: {link}')
        link.symlink_to(target)
        if name == executable:
            binary = target
    if binary is None:
        raise ValueError('Eseguibile principale mancante dai percorsi dichiarati')
    return binary


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
    unsupported = [a['id'] for a in lock['applications'] if arch not in a['assets']]
    if unsupported:
        parser.error('Release ufficiale non disponibile per ' + arch + ': ' + ', '.join(unsupported) + '. Usare linux/amd64.')
    installed = []
    args.bin_dir.mkdir(parents=True, exist_ok=True)
    for app in lock['applications']:
        asset = app['assets'][arch]
        print(f'Installazione {app["id"]} {app["version"]} ({arch})', flush=True)
        destination = args.root / 'apps' / app['id']
        with tempfile.TemporaryDirectory(prefix='artcraft-install-') as temp:
            for resource in app.get('resources', []):
                resource_archive = Path(temp) / resource['name']
                download(resource, resource_archive)
                if resource.get('kind') == 'debian':
                    install_deb(resource, resource_archive)
                else:
                    target = args.root / resource['install_path']
                    if not target.resolve().is_relative_to(args.root.resolve()):
                        raise ValueError('Resource outside installation root')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(resource_archive, target)
            archive = Path(temp) / asset['name']
            download(asset, archive)
            if app.get('install'):
                binary = install_toolkit(app, archive, destination, args.root, args.bin_dir, arch)
            else:
                safe_extract(archive, destination)
                binary = install_binaries(app, destination, args.bin_dir)
        installed.append({'id': app['id'], 'version': app['version'], 'binary': str(binary), 'sha256': asset['sha256']})
    shutil.rmtree('/var/lib/apt/lists', ignore_errors=True)
    (args.root / 'installed.json').write_text(json.dumps(installed, indent=2) + '\n')
    print(f'Installate {len(installed)} CLI.', flush=True)


if __name__ == '__main__':
    main()

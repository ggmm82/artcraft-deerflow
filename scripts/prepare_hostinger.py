#!/usr/bin/env python3
"""Generate a Compose release using one published commit for every runtime."""
import argparse
from pathlib import Path
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]


def prepare(commit, output, template=ROOT / 'config/compose.hostinger.template.yaml', inspect=None, images=None):
    if not re.fullmatch(r'[a-f0-9]{40}', commit):
        raise ValueError('Occorre lo SHA completo del commit con CI superata')
    content = yaml.safe_load(Path(template).read_text())
    supplied = images
    images = {}
    for service in ('gateway', 'frontend', 'sandbox-image'):
        prefix = content['services'][service]['image'].split('@')[0].split(':')[0]
        component = 'sandbox' if service == 'sandbox-image' else service
        image = supplied[component] if supplied is not None else prefix + ':sha-' + commit
        if supplied is not None and not re.fullmatch(re.escape(prefix) + r'@sha256:[a-f0-9]{64}', image):
            raise ValueError('Occorre il digest verificato del componente: ' + component)
        images[service] = image
        if inspect is None:
            subprocess.run(['docker', 'manifest', 'inspect', image], check=True,
                           stdout=subprocess.DEVNULL, timeout=120)
        else:
            inspect(image)
    # No output is written if any of the three published images is missing.
    for service, image in images.items():
        content['services'][service]['image'] = image
    content['services']['gateway']['environment']['STUDIO_SANDBOX_IMAGE'] = images['sandbox-image']
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('# Immagini pubblicate del commit: ' + commit + '\n' + yaml.safe_dump(content, sort_keys=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', help='SHA sorgente; ricavato dal manifest se omesso')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, help='Manifest dei digest verificati dalla CI')
    args = parser.parse_args()
    images = None
    if args.manifest:
        import json
        manifest = json.loads(args.manifest.read_text())
        images = manifest['images']
        if args.commit and args.commit != manifest['source_commit']:
            parser.error('Il commit deve corrispondere al manifest')
        args.commit = manifest['source_commit']
    if not args.commit:
        parser.error('Specificare --manifest (oppure --commit per i vecchi tag SHA)')
    prepare(args.commit, args.output, images=images)


if __name__ == '__main__':
    main()

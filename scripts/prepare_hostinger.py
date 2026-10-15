#!/usr/bin/env python3
"""Generate a Compose release using one published commit for every runtime."""
import argparse
from pathlib import Path
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]


def prepare(commit, output, template=ROOT / 'compose.hostinger.yaml', inspect=None):
    if not re.fullmatch(r'[a-f0-9]{40}', commit):
        raise ValueError('Occorre lo SHA completo del commit con CI superata')
    content = yaml.safe_load(Path(template).read_text())
    images = {}
    for service in ('gateway', 'frontend', 'sandbox-image'):
        image = content['services'][service]['image'].split(':')[0] + ':sha-' + commit
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
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.commit, args.output)


if __name__ == '__main__':
    main()

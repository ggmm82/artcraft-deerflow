#!/usr/bin/env python3
"""Validate catalog, schemas and Compose wiring without provider requests."""
import ast
import json
from pathlib import Path
import re
import runpy
import yaml

ROOT = Path(__file__).resolve().parents[1]

def main():
    lock=json.loads((ROOT/'versions.lock.json').read_text())
    cfg=yaml.safe_load((ROOT/'config/deerflow.yaml').read_text())
    local=yaml.safe_load((ROOT/'docker-compose.yaml').read_text())
    remote=yaml.safe_load((ROOT/'config/compose.hostinger.template.yaml').read_text())
    agy=json.loads((ROOT/'scripts/antigravity.lock.json').read_text())
    assert lock['cli_runtimes']['antigravity']==lock['cli_runtimes']['gemini']==agy['version']
    assert all(p['version']==agy['version'] for p in agy['platforms'].values())
    npm=json.loads((ROOT/'config/toolkit/package-lock.json').read_text())
    browser=next(a['version'] for a in lock['applications'] if a['id']=='playwright')
    assert npm['packages']['']['dependencies']['@playwright/test']==browser
    assert npm['packages']['node_modules/@playwright/test']['version']==browser
    ids={a['id'] for a in lock['applications']}
    assert len(ids)==len(lock['applications']) and ids==set(cfg['subagents']['custom_agents'])
    expected_skills={'artcraft-'+identifier for identifier in ids}|{'artcraft-workspace','artcraft-studio'}
    assert {p.parent.name for p in (ROOT/'skills/custom').glob('*/SKILL.md')}==expected_skills
    assert ids == set(runpy.run_path(str(ROOT/'scripts/acceptance.py'))['CASES'])
    assert (ROOT/'studio/deerflow.yaml').read_bytes()==(ROOT/'config/deerflow.yaml').read_bytes()
    assert (ROOT/'studio/versions.lock.json').read_bytes()==(ROOT/'versions.lock.json').read_bytes()
    for a in lock['applications']:
        for resource in a.get('resources', []):
            assert re.fullmatch('[a-f0-9]{64}', resource['sha256']) and resource['size_bytes'] > 0
            assert resource.get('license') and resource.get('source')
            assert resource['url'].startswith(('https://deb.debian.org/debian/pool/', 'https://huggingface.co/ggerganov/whisper.cpp/resolve/'))
            if resource.get('kind') == 'file':
                assert re.fullmatch('[a-f0-9]{40}', resource['revision']) and resource['revision'] in resource['url']
                assert '..' not in Path(resource['install_path']).parts and not Path(resource['install_path']).is_absolute()
        if a.get('install', {}).get('kind') == 'debian':
            assert all(v.get('package') and v.get('package_version') for v in a['assets'].values())
        for asset in a['assets'].values():
            assert re.fullmatch('[a-f0-9]{64}',asset['sha256'])
            assert asset['url'].startswith(a.get('download_base', a['repository']+'/releases/download/'+a['version']+'/'))
        skill=ROOT/'skills/custom'/('artcraft-'+a['id'])/'SKILL.md'
        assert skill.is_file()
        assert (skill.parent/'references/CLI-RECIPE.md').is_file()
        assert (skill.parent/'references/CAPABILITIES.md').is_file(), f'Mappa capacità mancante: {skill}'
        assert (skill.parent/'references/QUALITY.md').is_file(), f'Criteri professionali mancanti: {skill}'
        assert '## Consegna: sorgenti modificabili e compatibilità' in skill.read_text(), f'Contratto sorgenti mancante: {skill}'
        assert 'delivery' in (skill.parent/'references/CLI-RECIPE.md').read_text()
        front=yaml.safe_load(skill.read_text().split('---',2)[1])
        assert front['name']==skill.parent.name and front['description']
        for path in [skill, skill.parent/'references/CLI-RECIPE.md']:
            assert '/opt/artcraft/bin/' not in path.read_text(), f'Percorso CLI inesistente: {path}'
    assert cfg['sandbox']['allow_host_bash'] is False
    assert cfg['subagent_runtime']['max_running']==1
    assert any(t['name']=='studio_delegate' for t in cfg['tools'])
    assert cfg['models'][0]['use']=='studio.codex_provider:StudioCodexChatModel'
    assert not any(t['name'] in ('bash', 'write_file', 'str_replace') for t in cfg['tools'])
    for compose in [local,remote]:
        assert compose['services']['gateway']['environment']['STUDIO_SANDBOX_IMAGE']==compose['services']['sandbox-image']['image']
        assert not any('.env' in str(s.get('env_file','')) for s in compose['services'].values())
        assert not any('docker.sock' in str(v) for name,s in compose['services'].items() if name!='gateway' for v in s.get('volumes',[]))
    for name in ['gateway','frontend']:
        assert lock['deerflow']['commit'] in local['services'][name]['build']['additional_contexts']['deerflow']
    custom={'gateway','frontend','sandbox-image'}
    assert 'proxy' not in remote['services']
    assert all('build' not in remote['services'][name] for name in custom)
    assert all(remote['services'][name]['image'].startswith('ghcr.io/ggmm82/artcraft-deerflow-') for name in custom)
    assert all(':sha-' in remote['services'][name]['image'] for name in custom)
    assert 'networks' not in remote
    assert not any('traefik.docker.network=' in label for name in ['gateway','frontend'] for label in remote['services'][name]['labels'])
    assert not any('ports' in remote['services'][name] for name in remote['services'])
    gateway_labels='\n'.join(remote['services']['gateway']['labels'])
    assert 'PathPrefix(`/api/langgraph/`)' in gateway_labels
    assert 'replacepathregex.regex=^/api/langgraph/(.*)' in gateway_labels
    assert 'replacepathregex.replacement=/api/$${1}' in gateway_labels
    caddy=(ROOT/'docker/Caddyfile').read_text()
    assert 'handle /api/langgraph/*' in caddy and 'uri replace /api/langgraph /api' in caddy
    for folder in ['scripts','studio','tests']:
        for path in (ROOT/folder).glob('*.py'):ast.parse(path.read_text(),str(path))
    print(f'OK: {len(ids)} specialisti, {len(expected_skills)} skills, checksum, profilo seriale, Compose locale/remoto e assenza socket nei worker.')

if __name__=='__main__':main()

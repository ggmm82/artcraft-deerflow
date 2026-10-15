#!/usr/bin/env python3
"""Validate catalog, schemas and Compose wiring without provider requests."""
import ast
import json
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]

def main():
    lock=json.loads((ROOT/'versions.lock.json').read_text())
    cfg=yaml.safe_load((ROOT/'config/deerflow.yaml').read_text())
    local=yaml.safe_load((ROOT/'docker-compose.yaml').read_text())
    remote=yaml.safe_load((ROOT/'compose.hostinger.yaml').read_text())
    ids={a['id'] for a in lock['applications']}
    assert len(ids)==13 and ids==set(cfg['subagents']['custom_agents'])
    assert len(list((ROOT/'skills/custom').glob('*/SKILL.md')))==15
    assert (ROOT/'studio/deerflow.yaml').read_bytes()==(ROOT/'config/deerflow.yaml').read_bytes()
    assert (ROOT/'studio/versions.lock.json').read_bytes()==(ROOT/'versions.lock.json').read_bytes()
    for a in lock['applications']:
        for asset in a['assets'].values():
            assert re.fullmatch('[a-f0-9]{64}',asset['sha256'])
            assert asset['url'].startswith(a['repository']+'/releases/download/'+a['version']+'/')
        skill=ROOT/'skills/custom'/('artcraft-'+a['id'])/'SKILL.md'
        assert skill.is_file()
        front=yaml.safe_load(skill.read_text().split('---',2)[1])
        assert front['name']==skill.parent.name and front['description']
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
    print('OK: 13 specialisti, 15 skills, checksum, profilo seriale, Compose locale/remoto e assenza socket nei worker.')

if __name__=='__main__':main()

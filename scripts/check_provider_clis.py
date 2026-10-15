#!/usr/bin/env python3
"""Check actual pinned CLI entry points; no credentials or provider requests."""
import subprocess


def main():
    contracts = [
        (['codex', '--version'], ['0.162.1']),
        (['codex', 'login', '--help'], ['--device-auth']),
        (['codex', 'exec', '--help'], ['--model', '--json', '--output-last-message',
             '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox']),
        (['agy', '--version'], ['1.3.5']),
        (['agy', '--help'], ['--print', '--output-format', '--model', '--add-dir',
                            '--json-schema', '--agent', '--disable-slash-commands',
                            '--print-timeout', '--dangerously-skip-permissions']),
        (['agy', 'models', '--help'], ['List available models']),
    ]
    for command, expected in contracts:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=90)
        text = result.stdout + result.stderr
        for token in expected:
            if token not in text:
                raise RuntimeError(f'{command}: contratto CLI mancante: {token}')
        print('OK:', ' '.join(command))


if __name__ == '__main__':
    main()

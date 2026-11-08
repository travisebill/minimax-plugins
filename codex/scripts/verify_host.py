#!/usr/bin/env python3
"""Read installed plugin and skill metadata through Codex app-server; no model calls."""
import argparse
import json
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / 'marketplace/.agents/plugins/marketplace.json'


def marketplace_names():
    """外掛清單取自 marketplace manifest，不另維一份硬編碼名單。

    少一份名單 = 少一個會被漏驗的外掛。名單只有一份來源時，
    新增外掛不必記得回來改這支腳本。
    """
    data = json.loads(MARKETPLACE.read_text(encoding='utf-8'))
    return tuple(entry['name'] for entry in data['plugins'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', default=shutil.which('codex'))
    args = parser.parse_args()
    if not args.codex:
        raise SystemExit('Codex CLI unavailable')
    names = marketplace_names()
    output = ROOT / 'validation'
    output.mkdir(exist_ok=True)
    messages = queue.Queue()
    # Stderr may contain host diagnostics; retain only locally, outside the package.
    with (output / 'app-server.stderr.log').open('w') as errors:
        process = subprocess.Popen([args.codex, 'app-server', '--stdio'],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=errors, text=True, bufsize=1)

        def reader():
            for line in process.stdout:
                try:
                    messages.put(json.loads(line))
                except json.JSONDecodeError:
                    pass

        threading.Thread(target=reader, daemon=True).start()
        next_id = 0

        def request(method, params):
            nonlocal next_id
            next_id += 1
            call_id = next_id
            process.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': call_id,
                                           'method': method, 'params': params}) + '\n')
            process.stdin.flush()
            deadline = time.monotonic() + 30
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(method)
                message = messages.get(timeout=remaining)
                if message.get('id') == call_id:
                    if 'error' in message:
                        raise RuntimeError(message['error'])
                    return message['result']

        try:
            init = request('initialize', {
                'clientInfo': {'name': 'minimax_plugin_verification', 'version': '1.0.0'},
                'capabilities': {'experimentalApi': True},
            })
            process.stdin.write('{"jsonrpc":"2.0","method":"initialized","params":{}}\n')
            process.stdin.flush()
            plugins = []
            for name in names:
                response = request('plugin/read', {
                    'pluginName': name,
                    'marketplacePath': str(ROOT / 'marketplace/.agents/plugins/marketplace.json'),
                })['plugin']
                summary = response['summary']
                assert summary['installed'] and summary['enabled'], summary
                expected = {name + ':' + p.parent.name for p in (ROOT / 'marketplace/plugins' / name / 'skills').glob('*/SKILL.md')}
                discovered = {s['name'] for s in response['skills']}
                assert expected == discovered, (expected, discovered)
                plugins.append({'name': name, 'installed': summary['installed'],
                                'enabled': summary['enabled'], 'version': summary.get('localVersion'),
                                'display_name': summary['interface']['displayName'],
                                'skill_names': sorted(discovered)})
            listed = request('skills/list', {'cwds': [str(ROOT)], 'forceReload': True})
            skills = [s for entry in listed['data'] for s in entry['skills']
                      if '/travis-codex-studios/' in s['path']]
            expected_count = sum(len(list((ROOT / 'marketplace/plugins' / name / 'skills').glob('*/SKILL.md'))) for name in names)
            assert len(skills) == expected_count, [(s['name'], s['path']) for s in skills]
            assert all(s['enabled'] for s in skills)
            package_errors = [e for entry in listed['data'] for e in entry['errors']
                              if 'travis-codex-studios' in e['path']]
            assert not package_errors, package_errors
            report = {'status': 'pass', 'host': init.get('userAgent'), 'plugins': plugins,
                      'enabled_skill_count': len(skills),
                      'skills': [{'name': s['name'],
                                  'plugin_cache_relative_path': s['path'].split('/travis-codex-studios/', 1)[1],
                                  'enabled': s['enabled']}
                                 for s in skills]}
            (output / 'host.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            print(json.dumps(report, ensure_ascii=False, indent=2))
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == '__main__':
    main()

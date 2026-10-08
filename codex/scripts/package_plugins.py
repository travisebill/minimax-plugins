#!/usr/bin/env python3
"""Validate and export the two local Codex plugins (requires PyYAML)."""
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / 'marketplace/plugins'
EXPECTED = {
    'learning-game-studio': {'learning-mechanics', 'learning-game-feel'},
    'three-kingdoms-focus-studio': {
        'yt-focus-music-pipeline', 'three-kingdoms-focus-music',
        'three-kingdoms-video-project', 'music3-instrumental-prompts',
        'three-kingdoms-music-review', 'three-kingdoms-vocal-single',
        'yt-publish-strategy', 'audio-reactive-waveform',
    },
}


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path):
    raw = path.read_bytes()
    assert not raw.startswith(b'\xef\xbb\xbf'), path
    assert raw.endswith(b'\n'), path
    return json.loads(raw, object_pairs_hook=unique_keys)


def contained_file(root, relative):
    path = (root / relative).resolve()
    assert path.is_relative_to(root.resolve()) and path.is_file(), (root, relative)
    return path


def validate_plugin(plugin, expected):
    portable = read_json(plugin / 'plugin.json')
    compat = read_json(plugin / '.codex-plugin/plugin.json')
    assert portable['name'] == compat['name'] == plugin.name
    assert re.fullmatch(r'\d+\.\d+\.\d+', portable['version'])
    for key in ('version', 'description', 'author', 'keywords'):
        assert portable[key] == compat[key], key
    assert not {'skills', 'mcpServers', 'apps', 'interface'} & portable.keys()
    interface = portable['extensions']['com.openai']['interface']
    assert interface == compat['interface']
    assert len(interface['shortDescription']) <= 30
    prompts = interface['defaultPrompt']
    assert isinstance(prompts, list) and 1 <= len(prompts) <= 3
    assert all(isinstance(p, str) and len(p) <= 128 for p in prompts)
    for key in ('logo', 'composerIcon', 'logoDark', 'composerIconDark'):
        if key not in interface:
            continue
        image = contained_file(plugin, interface[key]).read_bytes()
        assert image.startswith(b'\x89PNG\r\n\x1a\n')
        width, height = struct.unpack('>II', image[16:24])
        assert width == height and 48 <= width <= 4096
        assert len(image) <= 5 * 1024 * 1024
    skills = sorted((plugin / 'skills').glob('*/SKILL.md'))
    assert {p.parent.name for p in skills} == expected
    for skill in skills:
        content = skill.read_text()
        assert content.startswith('---\n')
        front = yaml.safe_load(content.split('---', 2)[1])
        assert front['name'] == skill.parent.name
        assert isinstance(front['description'], str) and 0 < len(front['description']) <= 1024
        ui = yaml.safe_load((skill.parent / 'agents/openai.yaml').read_text())
        assert 25 <= len(ui['interface']['short_description']) <= 64
        assert '$' + skill.parent.name in ui['interface']['default_prompt']
        assert ui.get('policy', {}).get('allow_implicit_invocation', True)
    for path in plugin.rglob('*'):
        assert not path.is_symlink(), path
        assert path.name not in {'.DS_Store', '__pycache__', '.git', 'node_modules', '.env'}
        assert not path.name.startswith('._'), path
        if path.suffix in {'.md', '.yaml', '.json'}:
            content = path.read_text()
            assert '[TODO:' not in content, path
            # Check actual Markdown links, not example output paths in code blocks.
            if path.suffix == '.md':
                for target in re.findall(r'\]\(([^)\s]+)\)', content):
                    if re.match(r'[a-z][a-z0-9+.-]*:', target) or target.startswith('#'):
                        continue
                    relative = target.split('#', 1)[0]
                    destination = (path.parent / relative).resolve()
                    assert destination.is_relative_to(plugin.resolve()), (path, target)
                    assert destination.is_file(), (path, target)
    return {'name': plugin.name, 'version': portable['version'], 'skills': sorted(expected)}


def write_zip(path, files):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for source, name in files:
            archive.write(source, name)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
    return {'file': path.name, 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    market = read_json(ROOT / 'marketplace/.agents/plugins/marketplace.json')
    assert market['name'] == 'travis-codex-studios'
    assert {p['name'] for p in market['plugins']} == set(EXPECTED)
    results = []
    for entry in market['plugins']:
        assert entry['source'] == {'source': 'local', 'path': './plugins/' + entry['name']}
        assert entry['policy'] == {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}
        assert entry['category']
        results.append(validate_plugin(PLUGINS / entry['name'], EXPECTED[entry['name']]))
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    archives = []
    for result in results:
        plugin = PLUGINS / result['name']
        path = dist / f"{plugin.name}-{result['version']}-codex.zip"
        files = [(p, str(p.relative_to(plugin.parent))) for p in sorted(plugin.rglob('*')) if p.is_file()]
        archives.append(write_zip(path, files))
    bundle = []
    for folder in ('marketplace', 'scripts'):
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                bundle.append((path, 'minimax-codex-plugins/' + str(path.relative_to(ROOT))))
    for name in ('README.md', 'spec.md', 'UPSTREAM.json'):
        path = ROOT / name
        if path.is_file():
            bundle.append((path, 'minimax-codex-plugins/' + name))
    for name in ('host.json', 'audio-smoke.json', 'portable-schema.json', 'verification.md', 'installed-integrity.json'):
        path = ROOT / 'validation' / name
        if path.is_file():
            bundle.append((path, 'minimax-codex-plugins/validation/' + name))
    archives.append(write_zip(dist / 'minimax-codex-plugins-bundle.zip', bundle))
    (dist / 'SHA256SUMS').write_text(''.join(f"{a['sha256']}  {a['file']}\n" for a in archives))
    report = {'status': 'pass', 'plugins': results, 'archives': archives}
    (ROOT / 'validation').mkdir(exist_ok=True)
    (ROOT / 'validation/package.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

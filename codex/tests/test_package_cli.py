"""Packaging CLI regression: exports are the public installation boundary."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class PackageCLI(unittest.TestCase):
    def test_archives_include_waveform_and_preserve_existing_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'codex'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('dist', '__pycache__'))
            result = subprocess.run([sys.executable, str(copy / 'scripts/package_plugins.py')],
                                    capture_output=True, text=True,
                                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            music = next(p for p in report['plugins'] if p['name'] == 'three-kingdoms-focus-studio')
            self.assertIn('audio-reactive-waveform', music['skills'])
            self.assertEqual(len(music['skills']), 8)
            learning = next(p for p in report['plugins'] if p['name'] == 'learning-game-studio')
            self.assertEqual(set(learning['skills']), {'learning-mechanics', 'learning-game-feel'})
            for archive in (f"three-kingdoms-focus-studio-{music['version']}-codex.zip",
                            'minimax-codex-plugins-bundle.zip'):
                with zipfile.ZipFile(copy / 'dist' / archive) as package:
                    names = package.namelist()
                    for suffix in ('SKILL.md', 'scripts/render_waveform.py', 'requirements.txt',
                                   'assets/gold-mirrored.json', 'references/local-setup.md'):
                        self.assertTrue(any(n.endswith('skills/audio-reactive-waveform/' + suffix) for n in names), suffix)
                    self.assertFalse(any('__pycache__' in n or n.endswith(('.mov', '.wav', '.mp3')) for n in names))


if __name__ == '__main__':
    unittest.main()

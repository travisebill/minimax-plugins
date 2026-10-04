#!/usr/bin/env python3
"""Register this local marketplace and install both plugins using the Codex CLI."""
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
codex = shutil.which('codex')
if not codex:
    raise SystemExit('Codex CLI is required. Install it before running this script.')
commands = [
    ['plugin', 'marketplace', 'add', str(root / 'marketplace'), '--json'],
    ['plugin', 'add', 'learning-game-studio@travis-codex-studios', '--json'],
    ['plugin', 'add', 'three-kingdoms-focus-studio@travis-codex-studios', '--json'],
    ['plugin', 'list', '--marketplace', 'travis-codex-studios', '--json'],
]
for args in commands:
    subprocess.run([codex, *args], check=True)

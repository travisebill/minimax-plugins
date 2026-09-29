#!/usr/bin/env python3
"""Read-only full-decode measurements. Writes a new JSON report, never audio."""
import argparse
import hashlib
import json
import math
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone


def run(args, timeout=1800):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}): {result.stderr[-3000:]}')
    return result


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def finite(value):
    number = float(value)
    return number if math.isfinite(number) else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('Output must be a new file; overwriting is disabled.')
    for binary in ('ffmpeg', 'ffprobe'):
        if not shutil.which(binary):
            raise RuntimeError(f'Required executable unavailable: {binary}')
    before = digest(source)
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(source)]).stdout)
    streams = [item for item in probe['streams'] if item['codec_type'] == 'audio']
    if len(streams) != 1:
        raise ValueError(f'Expected exactly one audio stream, found {len(streams)}; choose a source explicitly.')
    # loudnorm measures its INPUT and sends processed samples only to the null sink.
    # Silence events are threshold observations, not proof of unwanted dead air.
    filters = 'silencedetect=noise=-60dB:d=0.5,loudnorm=I=-16:TP=-1:LRA=11:print_format=json'
    decoded = run(['ffmpeg', '-hide_banner', '-nostdin', '-v', 'info', '-xerror', '-err_detect', 'explode', '-i', str(source), '-map', '0:a:0', '-af', filters, '-f', 'null', '-'])
    blocks = re.findall(r'\{\s*"input_i"[\s\S]*?\}', decoded.stderr)
    if len(blocks) != 1:
        raise RuntimeError('Could not identify a unique loudnorm measurement block.')
    raw = json.loads(blocks[0])
    events = []
    for line in decoded.stderr.splitlines():
        if 'silencedetect' not in line:
            continue
        values = {key: float(value) for key, value in re.findall(r'(silence_start|silence_end|silence_duration):\s*([-+0-9.eE]+)', line)}
        if values:
            events.append(values)
    if digest(source) != before:
        raise RuntimeError('Source changed during measurement; discard results and retry on a stable file.')
    report = {
        'schema_version': 1,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'source': {'path': str(source), 'sha256': before, 'bytes': source.stat().st_size},
        'tools': {name: run([name, '-version'], 15).stdout.splitlines()[0] for name in ('ffmpeg', 'ffprobe')},
        'format': probe['format'], 'audio_stream': streams[0],
        'full_decode': 'pass',
        'measurements': {'integrated_lufs': finite(raw['input_i']), 'true_peak_dbtp': finite(raw['input_tp']), 'loudness_range_lu': finite(raw['input_lra'])},
        'raw_loudnorm_input': {key: value for key, value in raw.items() if key.startswith('input_')},
        'silence_detection': {'threshold_dbfs': -60, 'minimum_duration_seconds': 0.5, 'events': events},
        'evidence': 'measured',
        'limitations': ['Non-finite measurements are null; see raw values.', 'Full decode pass means no errors reported under the configured decoder; it does not establish musical quality.', 'Silence events require contextual listening.', 'A positive reconstructed true peak is not proof of audible clipping.', 'No listening, instrument, key, BPM, vocal-absence or continuity assessment was performed.'],
        'listening_status': 'not-assessed', 'continuity_status': 'not-assessed',
    }
    with output.open('x', encoding='utf-8') as target:
        json.dump(report, target, ensure_ascii=False, indent=2, allow_nan=False)
        target.write('\n')
    print(json.dumps({'report': str(output), 'source_sha256': before, 'measurements': report['measurements']}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'Measurement failed: {error}', file=sys.stderr)
        sys.exit(1)

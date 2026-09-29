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


def sample_points(duration, count=5):
    """Evenly spaced analysis windows; the final window never runs past the end."""
    windows = []
    for index in range(count):
        start = round(duration * index / count, 2)
        if duration - start < 1.0:
            break
        windows.append({
            'index': index,
            'start_sec': start,
            'duration_sec': round(min(duration - start, 12.0), 2),
        })
    return windows


def band_mean_db(source, start, length, low, high):
    """Mean level of one band over one window. volumedetect needs -v info, not -v error."""
    result = run(['ffmpeg', '-v', 'info', '-nostdin', '-ss', f'{start}', '-t', f'{length}',
                  '-i', str(source), '-map', '0:a:0',
                  '-af', f'highpass=f={low},lowpass=f={high},volumedetect', '-f', 'null', '-'])
    match = re.search(r'mean_volume:\s*(-?[\d.]+|-inf)\s*dB', result.stderr)
    if not match or match.group(1) == '-inf':
        return None
    return float(match.group(1))


def band_floor_db(source, start, length, low, high, step=1.0):
    """Minimum/median/max of one-second sub-windows.

    A mean over a whole passage reports instrument brightness, because attack
    transients reach well into the top octave. A constant noise bed does not decay,
    so the minimum sub-window is the figure that isolates an actual floor. Measured
    contrast on a 174 s lo-fi track: sparse passage minimum -91 dB against -43 dB
    where the drum kit enters, a 48 dB separation.
    """
    samples = []
    offset = 0.0
    while offset < length - 0.5:
        value = band_mean_db(source, round(start + offset, 2), 1.0, low, high)
        if value is not None:
            samples.append(round(value, 1))
        offset += step
    if not samples:
        return None
    ordered = sorted(samples)
    return {
        'min_db': ordered[0],
        'median_db': ordered[len(ordered) // 2],
        'max_db': ordered[-1],
        'sub_windows': len(samples),
    }


def short_term_windows(source):
    """100 ms short-term loudness with timestamps. ebur128 prints 'M: x S: y  I: z LUFS',
    so the S value is followed by whitespace, not by the literal 'LUFS'."""
    ebu = run(['ffmpeg', '-hide_banner', '-nostdin', '-nostats', '-i', str(source),
               '-map', '0:a:0', '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    samples = []
    for line in ebu.stderr.splitlines():
        stamp = re.search(r'\bt:\s*([\d.]+)', line)
        value = re.search(r'\bS:\s*(-?[\d.]+|-inf)(?=\s)', line)
        if not stamp or not value or value.group(1) == '-inf':
            continue
        samples.append((float(stamp.group(1)), float(value.group(1))))
    return samples


def quietest_start(samples, window_seconds=10.0, floor_lufs=-60.0):
    """Start time of the lowest-median sustained stretch, ignoring digital silence.

    Band levels are only meaningful where something musical is absent: measuring a
    noise floor across a full drum section reports the drums instead.
    """
    usable = [(time, value) for time, value in samples if value > floor_lufs]
    if len(usable) < 20:
        return None
    span = int(window_seconds / 0.1)
    if span >= len(usable):
        return round(usable[0][0], 2)
    best = None
    for index in range(len(usable) - span + 1):
        chunk = usable[index:index + span]
        ordered = sorted(value for _, value in chunk)
        middle = ordered[len(ordered) // 2]
        if best is None or middle < best[0]:
            best = (middle, chunk[0][0])
    return round(best[1], 2) if best else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    parser.add_argument('--no-band-profile', action='store_true',
                        help='Skip the per-section band profile and short-term dynamics scan.')
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
    duration = float(probe['format']['duration'])
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

    band_profile = None
    short_term = None
    if not args.no_band_profile:
        samples = short_term_windows(source)
        quiet = quietest_start(samples)

        # Band levels, anchored on the quietest sustained stretch so the high-band
        # reading reflects a genuine floor rather than whatever instrument is playing.
        # The quietest stretch uses per-second minima; other positions use one mean.
        sections = []
        if quiet is not None:
            sections.append({'index': 0, 'label': 'quietest', 'start_sec': quiet, 'duration_sec': 10.0,
                             'high_band': band_floor_db(source, quiet, 10.0, 10000, 16000),
                             'low_band': band_floor_db(source, quiet, 10.0, 20, 60)})
        for index, window in enumerate(sample_points(duration), start=len(sections)):
            if quiet is not None and abs(window['start_sec'] - quiet) < 1.0:
                continue
            sections.append({
                **window, 'label': f'position_{index}',
                'high_band': {'median_db': band_mean_db(source, window['start_sec'], window['duration_sec'], 10000, 16000)},
                'low_band': {'median_db': band_mean_db(source, window['start_sec'], window['duration_sec'], 20, 60)},
            })
        low_medians = [item['low_band']['median_db'] for item in sections
                       if item['low_band'].get('median_db') is not None]
        quiet_high = next((item['high_band'] for item in sections
                           if item.get('label') == 'quietest'), None)
        band_profile = {
            'quietest_region_start_sec': quiet,
            'sections': sections,
            'high_band_at_quietest': quiet_high,
            'low_band_span_db': round(max(low_medians) - min(low_medians), 2) if low_medians else None,
        }

        # Short-term loudness windows (100 ms). Counts windows above the median, which
        # is the observable form of a sudden jump; a calm track wants zero.
        if samples:
            values = [value for _, value in samples]
            ordered = sorted(values)
            middle = ordered[len(ordered) // 2]
            short_term = {
                'window_seconds': 0.1,
                'windows_assessed': len(values),
                'min_lufs': ordered[0],
                'max_lufs': ordered[-1],
                'median_lufs': middle,
                'windows_above_median_3lu': sum(1 for value in values if value > middle + 3.0),
                'windows_above_median_6lu': sum(1 for value in values if value > middle + 6.0),
            }

    if digest(source) != before:
        raise RuntimeError('Source changed during measurement; discard results and retry on a stable file.')
    report = {
        'schema_version': 2,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'source': {'path': str(source), 'sha256': before, 'bytes': source.stat().st_size},
        'tools': {name: run([name, '-version'], 15).stdout.splitlines()[0] for name in ('ffmpeg', 'ffprobe')},
        'format': probe['format'], 'audio_stream': streams[0],
        'full_decode': 'pass',
        'measurements': {'integrated_lufs': finite(raw['input_i']), 'true_peak_dbtp': finite(raw['input_tp']), 'loudness_range_lu': finite(raw['input_lra'])},
        'raw_loudnorm_input': {key: value for key, value in raw.items() if key.startswith('input_')},
        'silence_detection': {'threshold_dbfs': -60, 'minimum_duration_seconds': 0.5, 'events': events},
        'band_profile': band_profile,
        'short_term_dynamics': short_term,
        'evidence': 'measured',
        'interpretation_guide': {
            'SCOPE': 'Every figure below is genre-relative. The reference values quoted in the field descriptions were measured on sparse, lo-fi, sleep-oriented material; they are illustrations of separation, not universal thresholds. A nylon-string bossa nova, a brass-forward jazz chart, or a close-mic folk recording will show a legitimately higher high-band floor and a wider short-term range than a sparse lo-fi passage. Compare a track against itself across its own sections, and against other tracks of the same genre and instrumentation. Never apply a cross-genre absolute as a pass/fail line.',
            'high_band_at_quietest': '10-16 kHz level across the lowest-median 10 second stretch of the track, reported as min/median/max of one-second sub-windows. The stretch is located automatically because a floor sampled across a full drum section reports the drums instead, and the minimum sub-window is used because attack transients reach into the top octave while a true noise bed does not decay. A min_db near digital silence argues against a continuous high-frequency bed in that passage. It still does not identify any source: a raised value can be cymbals, a bright synth, tape colour, or a real noise bed. Confirm by listening before regenerating.',
            'low_band_span_db': 'Difference between the loudest and quietest 20-60 Hz median readings across sampled positions. A wide span indicates the low end moves with the arrangement. A near-zero span indicates a fixed low-frequency bed, which may be authored bass or a rendering artifact; cross-check the outro, where authored content should decay.',
            'windows_above_median_3lu': 'Count of 100 ms windows more than 3 LU above the median. Non-zero values are the measurable form of a sudden level jump. Calm and sleep-oriented material normally reports zero here; variation that only goes downward is usually arrangement, not a defect.',
        },
        'limitations': [
            'Non-finite measurements are null; see raw values.',
            'Full decode pass means no errors reported under the configured decoder; it does not establish musical quality.',
            'Silence events require contextual listening.',
            'A positive reconstructed true peak is not proof of audible clipping.',
            'Band levels are computed from lossy sources as delivered; codec noise is included. Re-measure after decoding to a lossless intermediate before blaming the material for a high noise floor.',
            'These band and short-term figures are level observations, not identifications. They cannot say what a sound is, only how much of it there is. Any claim about a specific source (rain, crackle, voices) needs listening evidence.',
            'No listening, instrument, key, BPM, vocal-absence or continuity assessment was performed.',
        ],
        'listening_status': 'not-assessed', 'continuity_status': 'not-assessed',
    }
    with output.open('x', encoding='utf-8') as target:
        json.dump(report, target, ensure_ascii=False, indent=2, allow_nan=False)
        target.write('\n')
    print(json.dumps({'report': str(output), 'source_sha256': before, 'measurements': report['measurements'], 'short_term_dynamics': short_term}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'Measurement failed: {error}', file=sys.stderr)
        sys.exit(1)

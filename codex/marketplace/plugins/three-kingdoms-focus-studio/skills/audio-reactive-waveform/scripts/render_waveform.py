#!/usr/bin/env python3
"""Offline, audio-reactive gold bars. Produces silent ProRes 4444 with alpha."""
import argparse
import json
import math
import os

DEFAULT_STYLE = {
    'width': 640, 'height': 280, 'fps': 30, 'bars': 48, 'shape': 'mirrored',
    'top_color': [255, 214, 91], 'bottom_color': [242, 105, 67],
    'bar_width': 4.2 / 640, 'margin': 34 / 640, 'baseline': .5,
    'max_height': 113.4 / 280, 'min_height': 1.4 / 280,
    'attack': .68, 'release': .23,
}
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True, type=Path, help='Local music file (first audio stream)')
    p.add_argument('--output', required=True, type=Path, help='Destination .mov file')
    p.add_argument('--duration', type=float, help='Maximum seconds from start; omit for full song')
    p.add_argument('--style', type=Path, help='Style JSON; see references/style.md')
    p.add_argument('--width', type=int, help='Canvas width; overrides style')
    p.add_argument('--height', type=int, help='Canvas height; overrides style')
    p.add_argument('--fps', type=int, help='Frame rate; overrides style')
    p.add_argument('--overwrite', action='store_true', help='Explicitly replace an existing output')
    a = p.parse_args()
    style = dict(DEFAULT_STYLE)
    if a.style:
        try:
            supplied = json.loads(a.style.expanduser().read_text(encoding='utf-8'))
            if not isinstance(supplied, dict) or set(supplied) - set(style):
                p.error('Style must be a JSON object with documented keys only')
            style.update(supplied)
        except (OSError, ValueError) as exc:
            p.error(f'Cannot read style JSON: {exc}')
    for key in ('width', 'height', 'fps'):
        if getattr(a, key) is not None:
            style[key] = getattr(a, key)
        setattr(a, key, style[key])
    for key in ('width', 'height', 'fps', 'bars'):
        if type(style[key]) is not int:
            p.error(f'Style {key} must be an integer')
    if not (320 <= a.width <= 3840 and 140 <= a.height <= 2160):
        p.error('Canvas limits: width 320–3840, height 140–2160')
    if not 8 <= style['bars'] <= 96:
        p.error('bars must be 8–96')
    if style['shape'] not in ('mirrored', 'single'):
        p.error('shape must be mirrored or single')
    for key in ('top_color', 'bottom_color'):
        color = style[key]
        if not isinstance(color, list) or len(color) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in color):
            p.error(f'{key} must be three RGB integers, each 0–255')
    for key in ('bar_width', 'margin', 'baseline', 'max_height', 'min_height', 'attack', 'release'):
        value = style[key]
        try:
            valid_number = type(value) in (float, int) and math.isfinite(value)
        except OverflowError:
            valid_number = False
        if not valid_number:
            p.error(f'{key} must be a finite number')
    if not (0 < style['bar_width'] <= .1 and 0 <= style['margin'] < .45 and 0 < style['baseline'] < 1):
        p.error('Invalid bar_width, margin, or baseline; see style reference')
    available = min(style['baseline'], 1-style['baseline']) if style['shape'] == 'mirrored' else style['baseline']
    if not 0 < style['min_height'] <= style['max_height'] < available:
        p.error('Require 0 < min_height <= max_height < available canvas height')
    spacing = (1-2*style['margin'])/(style['bars']-1)
    if style['bar_width'] + 1/a.width >= spacing or style['margin'] <= style['bar_width']/2:
        p.error('Bars overlap or extend beyond canvas; reduce bar_width/bars or increase margin')
    if not (0 < style['attack'] <= 1 and 0 < style['release'] <= 1):
        p.error('attack and release must be in (0, 1]')
    a.style = style
    if a.duration is not None and (not math.isfinite(a.duration) or a.duration <= 0):
        p.error('--duration must be a finite positive number')
    if not (320 <= a.width <= 3840 and 140 <= a.height <= 2160):
        p.error('Canvas limits: width 320–3840, height 140–2160')
    if a.width % 2 or a.height % 2:
        p.error('Width and height must be even')
    if not 1 <= a.fps <= 60:
        p.error('--fps must be between 1 and 60')
    a.input = a.input.expanduser().resolve()
    a.output = a.output.expanduser().resolve()
    if not a.input.is_file():
        p.error('Input is not an existing local file')
    if a.output.suffix.lower() != '.mov':
        p.error('Output must use .mov; MP4 does not preserve this alpha export')
    if a.input == a.output:
        p.error('Input and output must be different files')
    if not a.output.parent.is_dir():
        p.error('Output folder must already exist')
    if a.output.exists() and not a.overwrite:
        p.error('Output already exists; choose another filename or explicitly use --overwrite')
    return a


def checked(command):
    r = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        raise RuntimeError(r.stderr.decode(errors='replace').strip() or 'FFmpeg command failed')
    return r.stdout


def render(a, np):
    sr, n, bars = 44100, 8192, a.style['bars']
    style = a.style
    # Only our unique temporary directory is ever cleaned up.
    with tempfile.TemporaryDirectory(prefix='.waveform-', dir=a.output.parent) as folder:
        tmp = Path(folder)
        pcm = tmp / 'audio.f32'
        cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-protocol_whitelist', 'file,pipe', '-i', str(a.input), '-map', '0:a:0']
        if a.duration is not None:
            cmd += ['-t', str(a.duration)]
        checked(cmd + ['-ac', '1', '-ar', str(sr), '-f', 'f32le', str(pcm)])
        samples = pcm.stat().st_size // 4
        if not samples:
            raise RuntimeError('No decodable audio samples found')
        audio = np.fromfile(pcm, dtype='<f4')
        if not np.isfinite(audio).all():
            raise RuntimeError('Audio contains non-finite samples')
        # Ceil includes the final fractional frame; output can exceed input by < 1/fps.
        count = math.ceil(samples * a.fps / sr)
        print(f'Analyzing {samples/sr:.2f}s; {count} frames at {a.fps} fps.', flush=True)
        freq = np.fft.rfftfreq(n, 1 / sr)
        edges = np.geomspace(55, 14000, bars + 1)
        bins = [(freq >= lo) & (freq < hi) for lo, hi in zip(edges[:-1], edges[1:])]
        # Dense low-frequency bands can be narrower than FFT resolution.
        for band, lo, hi in zip(bins, edges[:-1], edges[1:]):
            if not band.any():
                band[np.argmin(np.abs(freq - math.sqrt(lo * hi)))] = True
        window = np.hanning(n)
        padded = np.pad(audio, (n // 2, n))
        energy = np.empty((count, bars), dtype=np.float64)
        for frame in range(count):
            offset = round(frame * sr / a.fps)
            spectrum = np.abs(np.fft.rfft(padded[offset:offset+n] * window)) / (n / 2)
            energy[frame] = [np.sqrt(np.mean(spectrum[b] ** 2)) for b in bins]
        weighted = energy * (np.sqrt(edges[:-1] * edges[1:]) / 200) ** .32
        db = 20 * np.log10(weighted + 1e-8)
        ceiling = np.percentile(db, 98.5)
        target = np.clip((db - (ceiling - 48)) / 48, 0, 1) ** 1.35
        # Exact digital silence stays at the minimum line height.
        target[energy.max(axis=1) < 1e-10] = 0
        del padded, audio, weighted, energy, db
        movie = tmp / 'output.mov'
        command = ['ffmpeg', '-nostdin', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba',
                   '-s', f'{a.width}x{a.height}', '-r', str(a.fps), '-i', '-', '-an',
                   '-c:v', 'prores_ks', '-profile:v', '4', '-pix_fmt', 'yuva444p10le',
                   '-alpha_bits', '16', '-vendor', 'apl0', '-threads', '2', str(movie)]
        y = np.arange(a.height, dtype=float) + .5
        x = np.arange(a.width, dtype=float) + .5
        center = a.height * style['baseline']
        half_width = style['bar_width'] * a.width / 2
        margin = style['margin'] * a.width
        centers = np.linspace(margin, a.width - margin, bars)
        # Limit each bar to its own columns; same coverage as the original full-canvas mask.
        columns = [np.flatnonzero(np.abs(x-cx) < half_width+.5) for cx in centers]
        smooth = np.zeros(bars)
        # Preserve smoothing time in seconds when changing FPS (original calibrated at 30).
        attack, release = 1 - (1-style['attack'])**(30/a.fps), 1 - (1-style['release'])**(30/a.fps)
        with (tmp / 'encoder.log').open('wb') as log:
            encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log)
            try:
                for frame, row in enumerate(target):
                    smooth += np.where(row > smooth, attack, release) * (row - smooth)
                    heights = (style['min_height'] + smooth * (style['max_height']-style['min_height'])) * a.height
                    rgba = np.zeros((a.height, a.width, 4), np.uint8)
                    for cx, cols, half in zip(centers, columns, heights):
                        xa = np.clip(half_width + .5 - np.abs(x[cols]-cx), 0, 1)
                        bottom = center + half if style['shape'] == 'mirrored' else center
                        top = center - half
                        ya = np.minimum(np.clip(y-top+.5, 0, 1), np.clip(bottom-y+.5, 0, 1))
                        mask = ya[:, None] * xa[None, :]
                        blend = np.clip((y-top)/(bottom-top), 0, 1)
                        rgb = np.array(style['top_color'])[None,:]*(1-blend[:,None]) + np.array(style['bottom_color'])[None,:]*blend[:,None]
                        rgba[:, cols, :3] = np.where(mask[:,:,None] > 0, rgb[:,None,:], 0).astype(np.uint8)
                        rgba[:, cols, 3] = np.rint(mask*255).astype(np.uint8)
                    encoder.stdin.write(rgba.tobytes())
                    if (frame + 1) % (a.fps * 5) == 0 or frame + 1 == count:
                        print(f'Rendering {frame+1}/{count} ({100*(frame+1)/count:.0f}%)', flush=True)
                encoder.stdin.close()
                if encoder.wait() != 0:
                    raise RuntimeError('FFmpeg encoder failed')
            except BaseException:
                if encoder.poll() is None:
                    encoder.terminate()
                    encoder.wait()
                if encoder.stdin and not encoder.stdin.closed:
                    try:
                        encoder.stdin.close()
                    except BrokenPipeError:
                        pass
                message = (tmp / 'encoder.log').read_text(errors='replace').strip()
                if message:
                    print(message, file=sys.stderr)
                raise
        info = json.loads(checked(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(movie)]))
        streams = info.get('streams', [])
        if len(streams) != 1 or streams[0].get('codec_name') != 'prores' or not streams[0].get('pix_fmt', '').startswith('yuva'):
            raise RuntimeError('Output validation failed: expected silent ProRes with alpha')
        if a.overwrite:
            os.replace(movie, a.output)
        else:
            # Atomic no-clobber publication, including an output created during rendering.
            try:
                os.link(movie, a.output)
            except FileExistsError:
                raise RuntimeError('Output appeared during rendering; existing file was preserved')
            except OSError as exc:
                raise RuntimeError('Cannot finalize on this filesystem. Use a local APFS/NTFS/ext4 folder. ' + str(exc))
        print(f'Created: {a.output}\nSilent ProRes 4444, real alpha, {a.width}x{a.height}, {count/a.fps:.3f}s')


def main():
    a = arguments()
    try:
        import numpy as np
    except ImportError:
        print('Missing NumPy. Activate your virtual environment and run: python -m pip install -r requirements.txt', file=sys.stderr)
        return 1
    for command in ('ffmpeg', 'ffprobe'):
        if not shutil.which(command):
            print(f'Missing {command} in PATH. See references/local-setup.md.', file=sys.stderr)
            return 1
    try:
        render(a, np)
        return 0
    except KeyboardInterrupt:
        print('\nCancelled; temporary files cleaned up.', file=sys.stderr)
        return 130
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

"""Public CLI → MOV regression tests; generated tones only, no private assets."""
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
import math

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'render_waveform.py'


class RendererCLI(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix='waveform-test-')
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.audio = self.root / 'synthetic tone with spaces.wav'
        with wave.open(str(self.audio), 'wb') as f:
            f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            f.writeframes(b''.join(struct.pack('<h', int(14000*math.sin(2*math.pi*(440 if i < 13230 else 4000)*i/44100))) for i in range(26460)))
        self.output = self.root / 'output with spaces.mov'

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), '--input', str(self.audio), '--output', str(self.output), *args], capture_output=True, text=True)

    def require_media(self):
        if not all(shutil.which(c) for c in ('ffmpeg', 'ffprobe')):
            self.skipTest('Requires ffmpeg + ffprobe')
        try:
            import numpy
        except ImportError:
            self.skipTest('Requires numpy')

    def render(self, *extra):
        self.require_media()
        result = self.cli('--width', '320', '--height', '140', '--fps', '10', *extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_rejects_invalid_inputs_without_tracebacks(self):
        for options in (['--width', '0'], ['--duration', 'nan'], ['--height', '141'], ['--fps', '0']):
            with self.subTest(options=options):
                result = self.cli(*options)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(self.output.exists())

    def test_unknown_style_and_overlapping_bars_are_rejected(self):
        style = self.root / 'style.json'
        for data in ({'unknown': 1}, {'bars': 96, 'bar_width': .1}, {'bars': True}, {'top_color': [255, -1, 0]}, {'release': 0}, {'margin':10**400}):
            style.write_text(json.dumps(data))
            result = self.cli('--style', str(style))
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('Traceback', result.stderr)

    def test_existing_output_is_preserved(self):
        self.output.write_bytes(b'keep existing file')
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_bytes(), b'keep existing file')

    def test_default_is_silent_prores_alpha_and_audio_reactive(self):
        self.render()
        info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(self.output)]))
        self.assertEqual(len(info['streams']), 1)
        stream = info['streams'][0]
        self.assertEqual(stream['codec_name'], 'prores')
        self.assertEqual(stream['profile'], '4444')
        self.assertTrue(stream['pix_fmt'].startswith('yuva'))
        self.assertEqual(int(stream['nb_frames']), 6)
        self.assertAlmostEqual(float(stream['duration']), .6, places=3)
        import numpy as np
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(self.output), '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'])
        frames = np.frombuffer(raw, np.uint8).reshape(-1, 140, 320, 4)
        alpha = frames[..., 3]
        self.assertEqual(int(alpha.min()), 0)
        self.assertEqual(int(alpha.max()), 255)
        self.assertTrue(np.any((alpha > 0) & (alpha < 255)))
        self.assertFalse(np.array_equal(alpha[0], alpha[-1]))
        self.assertTrue(np.array_equal(alpha, alpha[:, ::-1, :]))
        self.assertEqual(list(self.root.glob('.waveform-*')), [])

    def test_single_green_style_duration_and_explicit_overwrite(self):
        self.output.write_bytes(b'replace only with permission')
        style = self.root / 'green single.json'
        style.write_text(json.dumps({'shape':'single', 'bars':24, 'baseline':.8, 'max_height':.6, 'top_color':[0,255,0], 'bottom_color':[0,255,0]}))
        self.render('--style', str(style), '--duration', '.21', '--overwrite')
        import numpy as np
        raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(self.output),'-f','rawvideo','-pix_fmt','rgba','-'])
        frames = np.frombuffer(raw,np.uint8).reshape(-1,140,320,4)
        self.assertEqual(len(frames), 3)
        self.assertFalse(frames[:,113:,:,3].any())
        visible = frames[frames[...,3] > 240, :3]
        self.assertTrue((visible[:,1] > 240).all())
        self.assertTrue((visible[:,[0,2]] < 15).all())

    def test_dense_bands_render_without_empty_frequency_warnings(self):
        style = self.root / 'dense.json'
        style.write_text(json.dumps({'bars':96, 'bar_width':.002}))
        result = self.render('--style',str(style),'--duration','.1')
        self.assertNotIn('RuntimeWarning',result.stderr)

    def test_help_without_third_party_packages(self):
        result = subprocess.run([sys.executable, '-S', str(SCRIPT), '--help'], capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('--style', result.stdout)

    def test_missing_numpy_has_actionable_message(self):
        result = subprocess.run([sys.executable,'-S',str(SCRIPT),'--input',str(self.audio),'--output',str(self.output)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Missing NumPy', result.stderr)
        self.assertNotIn('Traceback',result.stderr)


if __name__ == '__main__':
    unittest.main()

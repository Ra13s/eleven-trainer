import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from eleven_trainer.cli import main
from eleven_trainer.settings import decode
from eleven_trainer.trials import catalog, load_trial


def flight(row):
    return [row[key] for key in ('position', 'direction', 'spin')] + [
        row['speedAndRate'][part]['speed'] for part in ('raw', 'spread')]


class TrialTests(unittest.TestCase):
    def test_all_42_files_validate_with_matching_checksums(self):
        entries = catalog()
        self.assertEqual(len(entries), 14)
        for entry in entries:
            for pace in ('slow', 'normal', 'fast'):
                with self.subTest(id=entry['id'], pace=pace):
                    metadata, payload = load_trial(entry['id'], pace)
                    rows = decode(payload)['shots']['data']
                    self.assertTrue(all(row['isActive'] == 'True' for row in rows.values()))
                    self.assertEqual(len(rows), metadata['active_rows'])

    def test_cycles_match_all_single_shots_in_ten_then_two_order(self):
        singles = [next(iter(decode(load_trial(f'I{i:02}')[1])['shots']['data'].values())) for i in range(1, 13)]
        for code, count in [('R01', 12), ('N01', 4)]:
            rows = list(decode(load_trial(code)[1])['shots']['data'].values())
            expected = [flight(row) for repetitions in (10, 2) for row in singles[:count] for _ in range(repetitions)]
            self.assertEqual([flight(row) for row in rows], expected)
            self.assertEqual(len(rows), count*12)

    def test_paces_only_change_launch_interval(self):
        for entry in catalog():
            slow = decode(load_trial(entry['id'], 'slow')[1])
            for pace, gap in [('normal', '2.4'), ('fast', '1.8')]:
                variant = decode(load_trial(entry['id'], pace)[1])
                for row in variant['shots']['data'].values():
                    self.assertEqual(row['speedAndRate']['raw']['secondsPerLaunch'], gap)
                    row['speedAndRate']['raw']['secondsPerLaunch'] = '3'
                self.assertEqual(variant, slow)

    def test_preview_and_export_never_contact_adb(self):
        with tempfile.TemporaryDirectory() as folder, patch('eleven_trainer.trials.Adb', side_effect=AssertionError('ADB contacted')), patch('sys.stdout', new=io.StringIO()):
            self.assertEqual(main(['trial', 'R01', '--preview']), 0)
            output = Path(folder)/'trial.json'
            self.assertEqual(main(['trial', 'I05', '--pace', 'fast', '--output', str(output)]), 0)
            self.assertEqual(output.read_bytes(), load_trial('I05', 'fast')[1])

    def test_default_menu_selects_full_cycle(self):
        with patch('builtins.input', side_effect=['', '']), patch('sys.stdout', new=io.StringIO()) as output:
            self.assertEqual(main(['trial', '--preview']), 0)
            self.assertIn('Active rows: 144', output.getvalue())

    def test_bad_id_and_missing_device_do_not_install(self):
        with patch('eleven_trainer.trials.Adb', side_effect=AssertionError('ADB contacted')), patch('sys.stdout', new=io.StringIO()), patch('sys.stderr', new=io.StringIO()):
            self.assertEqual(main(['trial', '../calibration', '--preview']), 2)
            self.assertEqual(main(['trial', 'R01']), 2)

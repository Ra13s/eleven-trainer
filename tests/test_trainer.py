"""Synthetic data only: no personal export or community drill payload."""

from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from eleven_trainer.cli import main
from eleven_trainer.device import AdbError, REMOTE, install
from eleven_trainer.settings import FIELDS, build, decode, encode, validate


def fixture():
    row = {"DataName": "Synthetic A", "isActive": "True", "Description": "Not calibrated for play"}
    for group, fields in FIELDS.items():
        row[group] = {part: {field: "0" for field in fields} for part in ("raw", "spread")}
    row["speedAndRate"]["raw"].update(speed="5", secondsPerLaunch="3", PostDelay="0.2")
    row["spin"]["raw"]["topBottom"] = "8"
    other = deepcopy(row)
    other["DataName"] = "Synthetic B"
    other["spin"]["raw"]["topBottom"] = "-5"
    return {"settingsVersion": "1", "shuffle": "True", "ballCount": "2", "timeScale": "1",
            "extra": {"preserve": "yes"}, "shots": {"data": {"A": row, "B": other}}}


class FakeAdb:
    def __init__(self, original, failure=None):
        self.files = {REMOTE: original}
        self.failure = failure
        self.triggered = False
        self.events = []
        self.running = True
        self.rename_count = 0

    def ready(self):
        self.events.append("ready")

    def read(self, path=REMOTE):
        if self.failure == "stage" and path != REMOTE and not self.triggered:
            self.triggered = True
            return b"wrong bytes"
        return self.files[path]

    def stop(self):
        self.events.append("stop")
        self.running = False

    def start(self):
        self.events.append("start")
        self.running = True
        if self.failure in ("launch", "rollback") and not self.triggered:
            self.triggered = True
            raise AdbError("simulated launch failure")
        if self.failure == "rewrite" and not self.triggered:
            self.triggered = True
            changed = json.loads(self.files[REMOTE])
            changed["shuffle"] = "True"
            self.files[REMOTE] = encode(changed)

    def run(self, *args):
        self.events.append(args)
        if args[0] == "push":
            if self.failure == "rollback" and self.triggered:
                raise AdbError("simulated lost connection during rollback")
            self.files[args[2]] = Path(args[1]).read_bytes()
        elif args[:2] == ("shell", "mv"):
            self.rename_count += 1
            self.files[args[3]] = self.files.pop(args[2])
            if self.failure == "rename" and not self.triggered:
                self.triggered = True
                raise AdbError("rename succeeded but response was lost")
            if self.failure == "interrupt" and not self.triggered:
                self.triggered = True
                raise KeyboardInterrupt()
        elif args[:3] == ("shell", "rm", "-f"):
            self.files.pop(args[3], None)
        elif args[:2] == ("shell", "pidof"):
            return b"1234" if self.running else b""
        else:
            raise AssertionError(f"Unexpected fake command: {args}")
        return b""


class SequenceTests(unittest.TestCase):
    def test_full_phase_order_and_source_preserved(self):
        source = fixture()
        original = deepcopy(source)
        result = build(source)
        names = [row["DataName"].split()[-1] for row in result["shots"]["data"].values()]
        self.assertEqual(names, ["A"] * 10 + ["B"] * 10 + ["A"] * 2 + ["B"] * 2)
        self.assertEqual(source, original)
        self.assertEqual(result["shuffle"], "False")
        self.assertEqual(result["extra"], source["extra"])

    def test_duplicate_steps_not_deduplicated(self):
        rows = build(fixture(), ["A", "B", "A"], [1])["shots"]["data"].values()
        self.assertEqual([r["DataName"].split()[-1] for r in rows], ["A", "B", "A"])

    def test_interval_preserves_physics_and_postdelay(self):
        source = fixture()
        result = build(source, ["A"], [1], 2.8)
        row = next(iter(result["shots"]["data"].values()))
        original = source["shots"]["data"]["A"]
        for group in ("position", "direction", "spin"):
            self.assertEqual(row[group], original[group])
        self.assertEqual(row["speedAndRate"]["raw"], {"speed": "5", "secondsPerLaunch": "2.8", "PostDelay": "0.2"})
        self.assertEqual(row["speedAndRate"]["spread"]["secondsPerLaunch"], "0")

    def test_active_selection_and_explicit_inactive(self):
        source = fixture()
        source["shots"]["data"]["B"]["isActive"] = "False"
        self.assertEqual(len(build(source, phases=[1])["shots"]["data"]), 1)
        result = build(source, ["B"], [1])
        self.assertEqual(next(iter(result["shots"]["data"].values()))["isActive"], "True")

    def test_invalid_selection_counts_interval_and_limit(self):
        for kwargs in ({"selections": ["missing"]}, {"phases": []}, {"phases": [0]},
                       {"phases": [-2]}, {"phases": [5001]}, {"interval": float("nan")}, {"interval": 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build(fixture(), **kwargs)

    def test_malformed_rows_rejected(self):
        for bad in (None, {}, [], {"settingsVersion": "2"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate(bad)
        for value in ("NaN", "Infinity", 5, None):
            source = fixture()
            source["shots"]["data"]["A"]["spin"]["raw"]["topBottom"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate(source)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            decode(b'{"settingsVersion":"1","settingsVersion":"2"}')


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.original = encode(fixture())
        self.candidate = encode(build(fixture(), ["A"], [1]))
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def test_success_and_exact_backup(self):
        adb = FakeAdb(self.original)
        report = install(adb, self.candidate, self.directory.name, wait_seconds=0)
        self.assertEqual(adb.files[REMOTE], self.candidate)
        self.assertEqual(Path(report["backup"]).read_bytes(), self.original)
        self.assertEqual(report["status"], "file_verified_after_launch")
        self.assertEqual(list(adb.files), [REMOTE])

    def test_bad_candidate_never_contacts_device(self):
        adb = FakeAdb(self.original)
        with self.assertRaises(ValueError):
            install(adb, b"{}", self.directory.name, wait_seconds=0)
        self.assertEqual(adb.events, [])

    def test_failure_before_rename_preserves_original(self):
        adb = FakeAdb(self.original, "stage")
        with self.assertRaisesRegex(AdbError, "not replaced"):
            install(adb, self.candidate, self.directory.name, wait_seconds=0)
        self.assertEqual(adb.files[REMOTE], self.original)
        self.assertEqual(adb.rename_count, 0)
        self.assertTrue(adb.running)

    def test_failures_after_replacement_restore_original(self):
        for failure in ("launch", "rename", "rewrite", "interrupt"):
            with self.subTest(failure=failure):
                adb = FakeAdb(self.original, failure)
                with self.assertRaisesRegex(AdbError, "Original settings restored"):
                    install(adb, self.candidate, self.directory.name, wait_seconds=0)
                self.assertEqual(adb.files[REMOTE], self.original)
                self.assertEqual(adb.rename_count, 2)

    def test_failed_rollback_keeps_local_original(self):
        adb = FakeAdb(self.original, "rollback")
        with self.assertRaisesRegex(AdbError, "ROLLBACK FAILED"):
            install(adb, self.candidate, self.directory.name, wait_seconds=0)
        backups = list(Path(self.directory.name).glob("*/original.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), self.original)


class CliTests(unittest.TestCase):
    def test_preflight_does_not_construct_adb(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.json"
            source.write_bytes(encode(fixture()))
            with patch("eleven_trainer.cli.Adb", side_effect=AssertionError("ADB touched")), patch("sys.stdout", new=io.StringIO()):
                self.assertEqual(main(["install", str(source), "--device", "placeholder", "--validate-only"]), 0)
                with patch("sys.stderr", new=io.StringIO()):
                    self.assertEqual(main(["install", str(source.with_name("missing.json")), "--device", "placeholder"]), 2)

    def test_real_module_with_absolute_input_and_no_overwrite(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "source.json", Path(folder) / "cycle.json"
            source.write_bytes(encode(fixture()))
            command = [sys.executable, "-m", "eleven_trainer", "build", str(source), str(output), "--shots", "A", "B", "--phases", "10", "2"]
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["active_rows"], 24)
            first = output.read_bytes()
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()

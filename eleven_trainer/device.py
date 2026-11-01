"""Explicit ADB transport and a recoverable settings replacement."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
import uuid

from .settings import decode, save_new

PACKAGE = "quest.eleven.forfunlabs"
REMOTE = f"/sdcard/Android/data/{PACKAGE}/settings/BallLauncherSettings.json"
ACTIVITY = f"{PACKAGE}/com.unity3d.player.UnityPlayerActivity"


class AdbError(RuntimeError):
    pass


class Adb:
    def __init__(self, executable="adb", port=5037, device=None):
        self.base = [str(executable), "-P", str(port)]
        if device:
            self.base += ["-s", device]

    def run(self, *args):
        try:
            result = subprocess.run(self.base + list(args), capture_output=True, timeout=40)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AdbError(f"Could not run ADB: {exc}") from exc
        if result.returncode:
            detail = (result.stderr or result.stdout).decode(errors="replace").strip()
            raise AdbError(f"ADB {args[0]} failed: {detail}")
        return result.stdout

    def ready(self):
        if self.run("get-state").strip() != b"device":
            raise AdbError("Device is not ready; check 'devices' and authorize USB debugging")

    def read(self, path=REMOTE):
        return self.run("exec-out", "cat", path)

    def stop(self):
        self.run("shell", "am", "force-stop", PACKAGE)

    def start(self):
        output = self.run("shell", "am", "start", "-n", ACTIVITY)
        if b"Error:" in output or b"Exception" in output:
            raise AdbError(output.decode(errors="replace"))


def install(adb, payload, backup_root, wait_seconds=7):
    """Validate before ADB, back up after stopping, verify stage and replacement.

    Any ambiguous rename result triggers a restore attempt. A lost connection
    can prevent rollback; the original remains available on the computer.
    """
    parsed = decode(payload)
    adb.ready()
    folder = Path(backup_root) / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    folder.mkdir(parents=True)
    original_path = folder / "original.json"
    candidate_path = folder / "candidate.json"
    before = adb.read()
    decode(before)
    save_new(folder / "before-stop.json", before)
    save_new(candidate_path, payload)
    temp = REMOTE + ".eleven-trainer-" + uuid.uuid4().hex
    stopped = False
    replacement_attempted = False
    original = None
    try:
        stopped = True  # Stop may succeed even if its response is lost.
        adb.stop()
        original = adb.read()
        decode(original)
        save_new(original_path, original)
        adb.run("push", str(candidate_path), temp)
        if adb.read(temp) != payload:
            raise AdbError("Staged bytes differ; original has not been replaced")
        replacement_attempted = True
        adb.run("shell", "mv", temp, REMOTE)
        if adb.read() != payload:
            raise AdbError("Installed bytes differ")
        adb.start()
        time.sleep(wait_seconds)
        if not adb.run("shell", "pidof", PACKAGE).strip():
            raise AdbError("Game did not stay running")
        after = adb.read()
        current = decode(after)
        if current["shots"]["data"] != parsed["shots"]["data"] or current["shuffle"] != parsed["shuffle"]:
            raise AdbError("Game changed the sequence after launch")
        save_new(folder / "readback.json", after)
        report = {"status": "file_verified_after_launch", "backup": str(original_path.resolve()),
                  "sha256": hashlib.sha256(payload).hexdigest(),
                  "note": "File verification only; observe placement, pacing and looping in the headset."}
        save_new(folder / "report.json", (json.dumps(report, indent=2) + "\n").encode())
        return report
    except (Exception, KeyboardInterrupt) as exc:
        recovery = []
        if replacement_attempted and original is not None:
            try:
                adb.stop()
                adb.run("push", str(original_path), temp)
                if adb.read(temp) != original:
                    raise AdbError("Rollback staging mismatch")
                adb.run("shell", "mv", temp, REMOTE)
                if adb.read() != original:
                    raise AdbError("Rollback readback mismatch")
                recovery.append("Original settings restored")
            except Exception as rollback_error:
                recovery.append(f"ROLLBACK FAILED: {rollback_error}; restore {original_path}")
        else:
            recovery.append("Original settings were not replaced")
        try:
            adb.run("shell", "rm", "-f", temp)
        except AdbError:
            recovery.append("Temporary remote file could not be removed")
        if stopped:
            try:
                adb.start()
            except AdbError:
                recovery.append("Open Eleven manually after restoring the connection")
        raise AdbError(f"{exc}. {'; '.join(recovery)}. Backups: {folder}") from exc

# Recover and troubleshoot

Use the reported error category to choose the action. A missing local JSON file is not evidence of a Quest connection problem.

| Symptom | Action |
|---|---|
| `Local file or settings error` / exit 2 | Check the source path with `validate`. Use an export in the supported format. A device connection cannot fix a missing file. |
| Output already exists | Choose a new output filename. Keep source exports and backups separate. |
| Unsupported settings version or missing fields | Stop. Save the original export locally and report the game version plus the field names; do not guess a new schema. |
| ADB executable missing | Run `where adb` on Windows; add Platform Tools to PATH or pass `--adb "C:\Tools\platform-tools\adb.exe"` on device commands. |
| `unauthorized` | Put on the awake headset and accept USB debugging. Reconnect USB if necessary. |
| No device listed | Check developer mode, a data-capable cable, USB port and Windows ADB driver. |
| More than one device | Use the exact transport serial with `--device`. USB and Wi-Fi can list the same physical headset twice. |
| Remote file missing | Open Eleven, save a Ball Machine change and close normally. If still absent, record the game version; the path may have changed. |
| Permission denied reading game settings | Verify developer authorization. If the firmware blocks access, stop and report it; the tool has no root workaround. |
| Wi-Fi offline or authentication failure | Re-establish authorized USB access, then follow [Wi-Fi setup](wifi.md). |
| Installed file changed after launch | The installer attempts rollback. Read its recovery message; keep the backup and report the game version. |
| `ROLLBACK FAILED` | Restore device access, then manually install the saved original as below. The tool cannot restore through a lost connection. |

## Restore a backup

Find the `backup` path printed by the successful install, or the backup folder named in a failure. Prefer its `original.json`: this is the saved settings file captured after the game stopped. `before-stop.json` is an additional earlier snapshot, available even if the later read failed.

Replace the example timestamp and serial with your own:

```console
python -m eleven_trainer validate .local/backups/TIMESTAMP-ID/original.json
python -m eleven_trainer install .local/backups/TIMESTAMP-ID/original.json --device YOUR_SERIAL
```

Restoring uses the same validation, backup and installation flow, and creates a new backup of the settings it replaces. Wait for the report, then inspect Ball Machine in the headset.

If a rollback verified the file but Eleven could not restart, open Eleven manually after fixing the connection. If you only have `before-stop.json`, use it in the same commands; it may omit changes the game saved during shutdown.

## Report a reproducible problem

Include the tool version (`--version`), Python version, OS, Quest model, game version, command with private identifiers replaced, and error text. State whether the failure happened before transfer, during transfer, after launch, or during actual ball playback.

Do not attach a full personal export or backup by default. Reduce the issue to a synthetic example where possible; remove serials, IP addresses and personal file paths. See [contributing](../../CONTRIBUTING.md).

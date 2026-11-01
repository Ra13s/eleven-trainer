# Command-line reference

Invocation: `python -m eleven_trainer COMMAND ...` or the installed `eleven-trainer COMMAND ...` entry point. Python 3.11+ is required. Paths are relative to the current working directory unless absolute. Quote paths containing spaces.

| Command | Arguments | Result |
|---|---|---|
| `--help` | — | Top-level help |
| `--version` | — | Package version |
| `list SOURCE` | Settings JSON path | Every row's ID, active flag and display name, in stored order |
| `validate SOURCE` | Settings JSON path | Schema preflight and summary; no ADB |
| `build SOURCE OUTPUT` | Options below | A new settings file; no ADB |
| `devices` | Transport options below | Raw `adb devices -l` listing |
| `pull OUTPUT --device SERIAL` | Transport options | Reads and validates the headset file, saves a new local copy; does not stop the game |
| `install SOURCE --device SERIAL` | Transport and install options | Validates, backs up, stops/restarts Eleven, transfers and verifies |

Command-specific help: `python -m eleven_trainer build --help`. Options belong **after** the subcommand.

## Build options

| Option | Default | Meaning |
|---|---|---|
| `--shots ID [ID ...]` | All active source rows | Ordered selection; explicit selection can include an inactive row, which becomes active in the output. Duplicate IDs remain separate steps. |
| `--phases N [N ...]` | `10 2` | Positive integer repeats per step in each phase |
| `--interval SECONDS` | Preserve source timing | Positive finite float; sets raw `secondsPerLaunch` and zeroes its spread |

All generated rows are active and `shuffle` is the string `False`. There is no inferred grouping by exercise title. Source files are not modified. Output creation fails if the file exists. Parent output directories are created as needed. Maximum generated rows: 5,000, a local resource guard rather than a confirmed game limit.

## Transport options

Available only on `devices`, `pull` and `install`:

| Option | Default | Meaning |
|---|---|---|
| `--adb PATH` | `adb` from PATH | Executable path |
| `--adb-port PORT` | `5037` | Computer-side ADB server port |
| `--device SERIAL` | Required on `pull`/`install` | Exact USB serial or connected `IP:port`; unavailable on `devices` |

The CLI does not run `adb connect` or auto-select a headset. Each ADB subprocess has a 40-second timeout. It uses argument lists, not a local shell. Installation waits seven seconds after launching the game before reading back the file.

## Install options and backup files

| Option | Default | Meaning |
|---|---|---|
| `--backup-dir PATH` | `.local/backups` | Parent directory for unique UTC timestamp/ID folders |
| `--validate-only` | Off | Runs source validation and returns before creating an ADB client; `--device` remains a required syntax argument |

An install creates these files as it progresses. A failed operation may leave only a subset.

| File | Contents |
|---|---|
| `before-stop.json` | Remote bytes read before stopping Eleven |
| `candidate.json` | Exact validated payload to be transferred |
| `original.json` | Remote bytes after stopping Eleven; rollback source |
| `readback.json` | Remote bytes after successful launch verification |
| `report.json` | Status, absolute backup path, SHA-256 of candidate, verification limitation |

The report's `file_verified_after_launch` status confirms byte equality before launch, a running game process after launch, and matching shot data and shuffle after launch. It does not assert that the game preserved every global field or that a user started Ball Machine.

## Summary fields

`validate` and `build` print `rows`, `active_rows`, `shuffle` and `nominal_interval_sum_seconds`. The last field sums raw launch intervals of active rows. It excludes `PostDelay`, random spreads, time scaling and runtime behavior, and is **not a measured session duration**.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Command completed |
| `2` | Argument error, local filesystem error, JSON/schema error or invalid selection |
| `3` | ADB/device operation or transaction failed; inspect the recovery message |

## Fixed game identifiers

- Package: `quest.eleven.forfunlabs`
- Activity: `quest.eleven.forfunlabs/com.unity3d.player.UnityPlayerActivity`
- Settings: `/sdcard/Android/data/quest.eleven.forfunlabs/settings/BallLauncherSettings.json`

These are compatibility assumptions based on the original workflow, not a public game API contract.

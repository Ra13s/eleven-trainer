# Try the complete independent pack

**Known hardware failure, reported 2026-11-01:** the default v0.2.0 mapping placed the launcher above the table on Quest 3. The installation/readback succeeded, but the in-game position was wrong. The older training pack was restored. The instructions below document the experiment; its default mapping needs correction before another practice test.

This download includes **42 preset files**: 12 individual feeds and two 10/2 cycles, each at three launch cadences. The files are already generated. You do not need to export or build a source pack first. Set up developer mode and ADB using [the first-training tutorial](../tutorials/first-training.md) if needed.

These are experimental feeds derived from a declared ballistic model. Native coordinates and spin mappings still need in-game calibration. They are not the older community-derived library and are not legal two-bounce serves. Read the [model and limits](../explanation/independent-model.md) for the derivation.

## Install the entire 10/2 cycle

From the extracted project folder, replace `YOUR_SERIAL` with your connected Quest's serial or Wi-Fi `IP:port`:

```console
python -m eleven_trainer trial R01 --preview
python -m eleven_trainer trial R01 --device YOUR_SERIAL
```

`R01` contains **144 active rows**: I01 ten times, I02 ten times, through I12 ten times; then I01 twice, I02 twice, through I12 twice. Shuffle is off. Observe whether your game loops back to the beginning after the last row; this is not established by a successful file transfer.

Each installation backs up and replaces Ball Machine settings and restarts Eleven. The report prints the backup path. Open Ball Machine in the headset and start it. Pay attention to the launcher side, direction of travel, net clearance, landing position and the phase labels.

## Choose pace

| Pace | Launch interval | R01 nominal interval sum |
|---|---:|---:|
| `slow` (default) | 3.0 s | 432 s / 7 min 12 s |
| `normal` | 2.4 s | 345.6 s / 5 min 45.6 s |
| `fast` | 1.8 s | 259.2 s / 4 min 19.2 s |

These are interval sums, not measured game durations. The pace changes only the time between launches; ball speed and spin stay the same.

```console
python -m eleven_trainer trial R01 --pace normal --device YOUR_SERIAL
python -m eleven_trainer trial R01 --pace fast --device YOUR_SERIAL
```

## Select one feed or a smaller cycle

| ID | Feed / session |
|---|---|
| I01 | Neutral spin, forehand, shorter |
| I02 | Neutral spin, backhand, shorter |
| I03 | Neutral spin, forehand, deeper |
| I04 | Neutral spin, backhand, deeper |
| I05 | Topspin hypothesis, forehand |
| I06 | Topspin hypothesis, backhand |
| I07 | Backspin hypothesis, forehand |
| I08 | Backspin hypothesis, backhand |
| I09 | Positive sidespin hypothesis, forehand |
| I10 | Negative sidespin hypothesis, forehand |
| I11 | Positive sidespin hypothesis, backhand |
| I12 | Negative sidespin hypothesis, backhand |
| N01 | I01–I04, each ten times then each twice: 48 active rows |
| R01 | I01–I12, each ten times then each twice: 144 active rows |

Forehand/backhand assumes a right-handed receiver and the provisional coordinate mapping. Signed sidespin labels do not yet claim which way the ball bends in Eleven.

For example:

```console
python -m eleven_trainer trial I07 --device YOUR_SERIAL
python -m eleven_trainer trial N01 --pace normal --device YOUR_SERIAL
```

For an interactive selection, run `TRIALS.cmd --device YOUR_SERIAL` on Windows, or:

```console
python -m eleven_trainer trial --device YOUR_SERIAL
```

Press Enter at both prompts to choose R01 at slow pace. Individual Windows launchers are also in `Trials/`; pass the same `--device` and optional `--pace` arguments.

## Export or inspect the settings

```console
python -m eleven_trainer trial R01 --pace normal --output .local/full-trial.json
python -m eleven_trainer validate .local/full-trial.json
```

Export and preview do not contact a device. The bundled JSON files live under `eleven_trainer/experimental/`; `catalog.json` records each variant's checksum. Files without a pace suffix are the slow variants. Edit an exported copy for personal changes; bundled-file changes require regenerating the catalog.

## Restore and report observations

Use the printed `original.json` backup with the [restore guide](recover.md#restore-a-backup). Keep the backup from **before the first experimental install** if you switch between trials: later backups may themselves contain experiments.

For feedback, note the row/ID, pace, whether the ball launches from the correct side, whether it clears the net, where it lands, and which direction it bends. A complete 10/2 pass checks ordering; separate observed flight errors from row-order errors. If every row goes the wrong direction, correct the coordinate mapping before tuning individual shots.

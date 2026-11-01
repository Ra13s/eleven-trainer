# Settings and compatibility

## Accepted input

The current reader accepts the observed `settingsVersion: "1"` format. JSON numbers inside shot parameters are **strings**, and booleans are the case-sensitive strings `"True"` and `"False"`. Duplicate JSON object keys are rejected. The root must contain `shuffle` and a nonempty `shots.data` object with at least one active row. Maximum accepted rows: 5,000.

Each row requires `DataName`, `isActive`, and the following numeric string fields in both its `raw` and `spread` objects:

| Group | Fields |
|---|---|
| `position` | `x`, `y`, `z` |
| `direction` | `horizontalAngle`, `verticalAngle` |
| `spin` | `topBottom`, `leftRight`, `screw` |
| `speedAndRate` | `speed`, `secondsPerLaunch`, `PostDelay` |

Values must be finite. Raw speed and launch interval must be positive; raw `PostDelay` must be nonnegative. Validation checks this supported structural contract, not table landing position, reachable ball speed, or the full game's internal constraints. Legacy exports organized under `drills` are unsupported.

## Transformation

`build` deep-copies the source and replaces `shots.data` with generated rows. Keys become `ET00001`, `ET00002`, and so on. For each phase, it iterates the ordered selections and appends the requested number of copies of each row. It never sorts or deduplicates selections.

Each generated row gets `isActive: "True"` and a `DataName` prefix with phase, step and repetition, for example `1.02 03/10`. Existing `Description` and unknown fields are preserved. Global `shuffle` becomes `"False"`.

With `--interval`, only raw `secondsPerLaunch` and its spread change, in addition to naming and active flags. Position, direction, spin, ball speed and their spreads remain as supplied. `PostDelay`, `timeScale`, `ballCount` and other global values are preserved. The tool does not use `ballCount` as a repetition counter; its precise game semantics have not been established here.

## Device transaction

1. Decode and validate the candidate locally before any device call.
2. Verify device state; read and save a validated pre-stop snapshot.
3. Stop Eleven; read and save a validated original.
4. Push a fixed local candidate snapshot to a unique temporary file beside the settings file.
5. Verify its bytes; rename it over the target; verify target bytes.
6. Launch Eleven; wait seven seconds; check process existence and shot data/shuffle readback.
7. Save the successful report.

Failures after an attempted replacement trigger a restore attempt using `original.json`, including when a rename might have succeeded but its response was lost. Connection loss or storage failure can prevent recovery. The error reports this and preserves local backup files. A restart is attempted after failures once stopping has been attempted. Do not run two installs concurrently against the same headset; there is no cross-process transaction lock.

## Compatibility and evidence

| Area | Evidence / status |
|---|---|
| Original personal workflow | Windows, Quest 3; observed Eleven version `0.436.37_2026.9.4.18.35.33.415` |
| New package | Offline unit/CLI tests and fake-device transactions; no completed hardware acceptance test yet |
| JSON import/build | Tested against synthetic fixtures and local exports from the original workflow; private exports are not bundled |
| File order | Python preserves insertion order; whether every future game build executes it identically needs hardware verification |
| End-of-list loop, phase timing, trajectory | Must be observed in Ball Machine; readback does not prove them |
| In-game instructions | Generated short names are written to `DataName`; long `Description` visibility is unverified |
| Other Quest models / firmware | Unverified |
| macOS/Linux ADB hardware use | Unverified; code uses portable Python APIs |
| Game AI changes or performance analysis | Not implemented |

Record new hardware observations with the exact game and headset versions. Do not broaden compatibility claims based only on passing offline tests.

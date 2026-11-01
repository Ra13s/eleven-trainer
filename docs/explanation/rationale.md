# Why Eleven Trainer exists

The project began with a practical training problem: a player wanted to learn different forehands, backhands, spins and serve returns, but a large list of changing shots was too difficult to follow. Faster automation did not help when none of the returns landed. Practice needed a comfortable starting shot, enough consecutive repetitions to understand it, and a deliberate move toward switching between shots.

## Repetition first, then transitions

A 10/2 cycle separates two demands. Ten copies of each shot give the player time to settle into a movement. A second pass with two copies of each asks them to recognize and switch more frequently. The sequence is `10 A → 10 B → … → 2 A → 2 B → …`; every selected step participates in both phases.

The numbers are a user-chosen training preference, not a scientifically validated prescription. A player can use `--phases 5 1`, practice one row, or choose a longer interval. The tool makes the schedule explicit and reproducible; it does not decide that someone has mastered a stroke.

Explicit duplicate rows were chosen because they can express this order using the observed settings format without relying on an undocumented repeat counter. The tradeoff is a longer list in the game's interface. A future native grouping feature could make that representation smaller if its behavior can be verified.

## Pace and difficulty are separate

“Make it faster” can mean launch more often or send a faster ball. Those changes are not interchangeable. A shorter gap increases the pace of practice while retaining the flight. Changing velocity, angle or spin can alter the bounce and landing point, making a previously returnable shot unsuitable.

The initial tool therefore preserves flight parameters. It changes repetition and, optionally, the launch interval. Calibration stays in Eleven, where the player can see the result. Source delays and other spread values remain intact, so a fixed interval alone is not a promise of perfectly uniform timing.

## A local file tool is a useful first step

Eleven's saved Ball Machine settings provide an observable interface. A local program can read a player's own file, make a reviewable derivative, and transfer it using ADB. There is no service to operate, recurring AI cost or remote training-data store. The game account and headset setup remain separate requirements.

The interface is unofficial. The game can change its schema, rewrite settings on exit, or refuse file access in a later firmware version. The installer stops the game before its final backup, stages a temporary file, verifies bytes and reads the result after launch. These steps reduce accidental loss; they cannot make an undocumented interface stable or guarantee rollback through a disconnected headset.

Installing between sessions costs a restart. It is an explicit tradeoff: this version does not promise seamless live switching or real-time adaptation. The generated cycle is intended for the game's own playback, whose loop behavior must be confirmed on the target version.

## Where AI could help later

An AI planner could turn “I struggle with backspin” into a progression using already calibrated shots, explain the goal of each stage, and suggest a next session from the player's feedback. The deterministic builder and validator would still be responsible for the file output.

Assessing technique requires evidence beyond settings: user reports, measured results, video or an appropriate game data source. A JSON row cannot tell whether a return landed. Rewriting the built-in AI opponent is a separate reverse-engineering problem and is outside this project.

Similarly, a “pendulum” label is a coaching reference to a serve family. Ball-machine settings can describe incoming spin and placement, but do not reproduce the opponent's arm motion or deception. Documentation should make that distinction clear instead of promising a realistic server simulation.

## A reusable project rather than a personal folder

The original setup coupled launchers to one computer's paths, a headset address and a curated library. Reorganizing that folder exposed a stale manifest path. The reusable tool accepts explicit file paths, shares the same local preflight between validation and installation, and uses no global preset manifest. Tests cover that boundary so an offline file error is reported before touching the device.

Personal presets and third-party packs are kept separate from source code. This lets people use their own calibration without publishing their device data or silently relicensing someone else's drills. See [sources and licensing](sources.md).

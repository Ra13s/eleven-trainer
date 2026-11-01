# Eleven Trainer

**Turn your Eleven Table Tennis ball-machine shots into repeatable practice sessions.**

Choose a single serve, work through a sequence, or build a complete **10/2 cycle**: ten repetitions of each selected shot, then two of each in the same order. Set the launch interval to suit your pace. Transfer the result to a Meta Quest with ADB, with a local backup and file verification.

Eleven Trainer is a local Python command-line tool, released under the [MIT license](LICENSE). No subscription, AI API key, or cloud account is required by the tool. Quest setup still requires a Meta account and developer access.

**Status: early alpha.** This package was extracted from a personal Windows/Quest 3 workflow and redesigned for reuse. The new package has automated offline tests; it has **not yet completed a hardware acceptance test**. The game's settings format is unofficial and can change. See [compatibility and evidence](docs/reference/settings.md#compatibility-and-evidence).

## Start here

| What you need | Read this |
|---|---|
| “I'm new. Take me from developer mode to my first session.” | [First training tutorial](docs/tutorials/first-training.md) |
| “I want one serve, a full cycle, or a different pace.” | [Create a session](docs/how-to/create-session.md) |
| “I want to unplug the USB cable.” | [Connect over Wi-Fi](docs/how-to/wifi.md) |
| “Something failed; I want my previous settings back.” | [Recover and troubleshoot](docs/how-to/recover.md) |
| “What does this command or JSON field mean?” | [CLI reference](docs/reference/cli.md) · [Settings reference](docs/reference/settings.md) |
| “Why build this, and why these design choices?” | [Rationale](docs/explanation/rationale.md) |

The [documentation](docs/index.md) follows [Diátaxis](https://diataxis.fr/): learning tutorials, task-oriented how-to guides, factual reference, and explanation each have their own place.

## What it does

- Imports the settings file from your own headset, or reads an existing local export.
- Lists shot IDs and names so you can choose precisely what to practice.
- Builds one-shot sessions and ordered repetition phases, preserving repeated selections.
- Preserves source trajectory, spin and speed; an optional interval changes launch frequency.
- Validates locally, then installs through a temporary remote file with backup, readback and attempted rollback on failure.
- Works with USB or an already connected Wi-Fi ADB device.

The tool does not rewrite Eleven's AI opponent, measure your technique, or adapt during play. It cannot reproduce a server's pendulum arm motion: a ball-machine row describes the incoming ball. Long coaching text inside the game's UI is not a verified feature. These boundaries are covered in the [rationale](docs/explanation/rationale.md).

## Install and try

Requirements: Python 3.11 or newer. Device commands additionally need [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools), an authorized Quest, and Eleven Table Tennis with saved ball-machine settings. Windows is the primary development platform; macOS/Linux hardware operation is unverified.

Download this repository with **Code → Download ZIP** and extract it, or clone it:

```console
git clone https://github.com/Ra13s/eleven-trainer.git
cd eleven-trainer
python -m venv .venv
```

On Windows, install into that environment without activating it:

```console
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m eleven_trainer --help
```

On macOS/Linux, use `.venv/bin/python` instead. The commands below use `python` as shorthand for the chosen environment's interpreter. Running `python -m eleven_trainer` directly from the repository also works without installation; the runtime uses only Python's standard library.

With your own exported settings at `.local/source.json`:

```console
python -m eleven_trainer list .local/source.json
python -m eleven_trainer build .local/source.json .local/cycle.json --phases 10 2 --interval 2.8
python -m eleven_trainer validate .local/cycle.json
```

This uses all active source rows in file order. For a beginner, start with **one known comfortable shot**; follow the [tutorial](docs/tutorials/first-training.md) for selection, headset setup and installation. No playable drill pack is bundled: use your own saved shots. [Why packs are separate](docs/explanation/sources.md).

## Development

```console
python -m unittest discover -s tests -v
python tools/check_docs.py
```

Tests cover ordering, source preservation, malformed input, local preflight, and installation failures using a fake ADB device. CI runs these checks on Windows and Ubuntu with Python 3.11 and 3.13. See [contributing](CONTRIBUTING.md) for the hardware acceptance checklist and documentation rules.

## License and relationship to Eleven

Original code and documentation in this repository are MIT licensed. Imported game settings and community drill packs retain their own ownership and terms; this license does not relicense them. The project includes no game binaries, ADB binaries, personal backups or private device identifiers.

Eleven Trainer is an independent community project, not affiliated with or endorsed by For Fun Labs or Meta. Eleven Table Tennis and Meta Quest names identify the products it works with.

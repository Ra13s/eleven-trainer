# Contributing

Use Python 3.11+ and run from the repository root:

```console
python -m unittest discover -s tests -v
python tools/check_docs.py
```

There are no runtime third-party dependencies. `python -m pip install -e .` installs the CLI entry point through setuptools. Do not commit `.local`, headset exports, backups, credentials, serial numbers, LAN addresses or absolute personal paths. Use synthetic fixtures when reporting bugs or adding tests.

## Change expectations

For sequence changes, test ordering and preservation of physics fields. For device changes, test failure paths before and after replacement, including an ambiguous rename and failed rollback. Keep local validation ahead of any ADB call. Never replace runtime checks with Python `assert`, which can be disabled.

Document the concrete behavior and test evidence. An offline test is not evidence of compatible game physics or successful hardware installation. Imported drill data needs documented provenance and redistribution permission before inclusion.

## Documentation

Use the [documentation plan](docs/documentation-plan.md) and [Diátaxis](https://diataxis.fr/). Put a guided first experience in tutorials, goal-specific procedures in how-to guides, exact options/fields in reference, and tradeoffs in explanation. Keep the README as the project entry point. Check code examples against CLI help and update the starting tutorial when its commands change.

For volatile Meta UI steps, link the official source and record the check date. Avoid asserting that an in-game menu or setting exists based only on a JSON field.

## Hardware acceptance checklist

This is a manual checklist, not an assertion that these checks have passed:

- Record Quest model, firmware, Eleven version, OS and tool version.
- Authorize USB ADB and export a known comfortable shot.
- Build a two-shot 10/2 session; inspect the generated ordering offline.
- Install with a backup and verify the reported readback.
- In Ball Machine, observe ten A, ten B, two A, two B, then verify the end-of-list behavior.
- Check placement, timing and row labels separately from file persistence.
- Restore `original.json`; confirm the previous settings in the headset.
- Repeat device transfer over Wi-Fi if documenting Wi-Fi compatibility.

Do not deliberately disconnect a user's headset during a real write to test rollback. Exercise destructive failure simulations with the fake transport in unit tests.

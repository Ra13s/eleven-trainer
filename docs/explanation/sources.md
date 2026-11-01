# Sources and provenance

Original code, documentation and the independently generated experimental pack are released under the [MIT license](../../LICENSE). Imported user settings remain separate data; the project license does not relicense external files.

## The bundled pack

The twelve experimental feed definitions were derived from declared geometry, gravity and new target/apex/spin-ratio choices. A fresh agent worked from the JSON schema without reading existing launch presets. The deterministic generator now lives in this repository; it produces the individual presets and their repetition/cadence variants. No community pack is downloaded or read during generation. See [the independent model](independent-model.md) for equations, assumptions and remaining calibration work.

The original personal workflow used imported trajectories. Those settings are not the numerical source of this bundled independent experiment, and that older private library is not included here. The tool still supports importing your own exports for separate sessions.

## Platform documentation

Setup instructions were checked on 2026-11-01 against [Meta Device Setup](https://developers.meta.com/vr/documentation/native/android/mobile-device-setup/), [Android ADB documentation](https://developer.android.com/tools/adb), and [Platform Tools downloads](https://developer.android.com/tools/releases/platform-tools). External setup instructions can change independently of this project.

The documentation structure follows [Diátaxis](https://diataxis.fr/). Learning, task completion, reference and explanation each have a separate place.

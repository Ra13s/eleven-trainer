# Your first training session

By the end, you will have exported your own ball-machine settings, selected one familiar shot, built a repeated session, and installed it with a recoverable backup. Use USB for this first lesson. Keep the headset awake during transfers.

You need a Quest with Eleven Table Tennis installed, a Windows computer, a USB data cable, a phone paired with the headset in the Meta Horizon app, and Python 3.11+. This tutorial's desktop commands use **Command Prompt (`cmd.exe`)**. No game APK modification or rooting is involved.

## 1. Enable developer access

Open the [Meta developer sign-up page](https://developers.meta.com/horizon/sign-up/) using the account that owns your headset. In the Developer Dashboard, join or create a developer team and complete account verification. Meta's current requirements include a verified account, age 18+, and no device restriction preventing developer mode. Follow Meta's verification screen for the available method.

On your phone, open **Meta Horizon → headset icon → your paired headset → Headset Settings → Developer Mode**, and enable it. If the switch is missing, check the signed-in account, team membership and verification. Menu labels can change; these steps were checked against [Meta's device setup documentation](https://developers.meta.com/vr/documentation/native/android/mobile-device-setup/) on 2026-11-01.

Connect the headset with a data-capable USB cable. Put it on and accept **Allow USB debugging**. Trust this computer persistently only if it is yours. A file-transfer permission dialog is a different permission. If no prompt appears, consult the same Meta setup page for the current Developer/MTP notification setting.

## 2. Install ADB and check the connection

Download the Windows archive from [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) and extract its `platform-tools` folder to `C:\Tools\platform-tools`. If you already have an SDK installation, use its existing folder instead. Full Android Studio is not needed for this tool.

Install the Windows ADB driver linked from [Meta's device setup guide](https://developers.meta.com/vr/documentation/native/android/mobile-device-setup/): extract the driver archive, right-click its `.inf` file, and choose Install.

Open Command Prompt and run:

```bat
set "PATH=C:\Tools\platform-tools;%PATH%"
adb version
adb devices -l
```

Expect one row with a serial and the state `device`. `unauthorized` means you still need to accept USB debugging in the headset. An empty list means the cable, driver or developer-mode setup needs attention. Resolve that before continuing with [troubleshooting](../how-to/recover.md).

For the rest of this tutorial, replace `YOUR_SERIAL` with that exact serial:

```bat
set "QUEST_SERIAL=YOUR_SERIAL"
adb -s "%QUEST_SERIAL%" get-state
```

The result should be `device`. ADB's connection and authorization model is described in the [official ADB documentation](https://developer.android.com/tools/adb).

## 3. Open Eleven and save a comfortable shot

In Eleven, open the Ball Machine and use its controls to save a shot you can already return comfortably. Try several balls before continuing. This first lesson uses that calibration; the tool does not know your skill level or invent a safe trajectory for you.

Leave the Ball Machine settings screen so the game can save. Close Eleven normally, keeping the headset awake. This gives the export a chance to reflect your latest changes. If no settings file exists, reopen Eleven and save a Ball Machine change before retrying.

## 4. Get Eleven Trainer

Download and extract this repository using GitHub's **Code → Download ZIP**, then open Command Prompt in the extracted directory. Alternatively, if Git is installed:

```console
git clone https://github.com/Ra13s/eleven-trainer.git
cd eleven-trainer
```

From that directory, create an isolated Python environment:

```bat
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m eleven_trainer --version
```

The version should be `0.1.0`. If `python` is missing, install it from [python.org](https://www.python.org/downloads/windows/) and reopen Command Prompt. Repeat the `PATH` and `QUEST_SERIAL` commands if you opened a new window.

## 5. Export and inspect your shots

```bat
.venv\Scripts\python -m eleven_trainer pull .local\source.json --device "%QUEST_SERIAL%"
.venv\Scripts\python -m eleven_trainer list .local\source.json
```

The first command saves a local copy. The second prints each shot's ID, active flag and name. Find the comfortable shot you just tried. Copy its **ID**, not its display name. This ID belongs to your file; no universal `forehand` ID exists.

```bat
set "SHOT_ID=PASTE_YOUR_SHOT_ID_HERE"
.venv\Scripts\python -m eleven_trainer build .local\source.json .local\first-session.json --shots "%SHOT_ID%" --phases 10 2 --interval 2.8
```

Expect **12 active rows**. They describe ten copies followed by two copies of your one shot. Its flight speed and spin are unchanged. The launch interval is set to 2.8 seconds; source `PostDelay` remains unchanged.

## 6. Validate and install

First run the same local preflight used by installation:

```bat
.venv\Scripts\python -m eleven_trainer install .local\first-session.json --device "%QUEST_SERIAL%" --validate-only
```

Expect `Local installer validation OK; no device contacted`. Now finish any live game: the next command **stops and restarts Eleven** and replaces its Ball Machine settings file.

```bat
.venv\Scripts\python -m eleven_trainer install .local\first-session.json --device "%QUEST_SERIAL%"
```

A successful report contains `file_verified_after_launch` and the path to `original.json` under `.local\backups`. Keep that backup. It holds the previous settings, captured after Eleven was stopped.

## 7. Observe the result in the headset

Open Ball Machine and start it. Check that the shot is familiar, the rows are active, and shuffle is off. Generated names begin with the phase and repetition, such as `1.01 01/10` and `2.01 01/02`.

Watch the transition after ten balls, then after the next two. Verify whether your game version loops back to the first row. The tool prepares an ordered list; file verification cannot establish what the game actually plays. If it stops or behaves differently, stop the launcher and record the game version and behavior before changing anything else.

You now know how to export, select, build and install a session. For two different shots and the full `10 A → 10 B → 2 A → 2 B` pattern, use [Create a session](../how-to/create-session.md). To undo the installation, use [Restore a backup](../how-to/recover.md#restore-a-backup).

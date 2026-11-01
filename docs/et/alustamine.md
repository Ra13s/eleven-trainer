# Esimene treening Questis

Selle õpetuse lõpuks oled salvestanud oma Ball Machine'i seadistused arvutisse, valinud ühe tuttava löögi ja paigaldanud sellest korduva harjutuse. Alustame USB kaudu. Hoia Quest ülekande ajal ärkvel.

Vaja on Windowsi arvutit, Python 3.11 või uuemat, andmesidet toetavat USB-kaablit, telefoni Meta Horizon rakendusega ning Questi, kus Eleven Table Tennis juba töötab. Käskude jaoks ava **Command Prompt / Käsuviip (`cmd.exe`)**.

## 1. Luba arendajarežiim

Mine oma Questi kontoga [Meta arendajalehele](https://developers.meta.com/horizon/sign-up/). Liitu arendajatiimiga või loo see ning kinnita konto vastavalt Meta juhistele. Seejärel ava telefonis **Meta Horizon → prillide ikoon → sinu Quest → Headset Settings → Developer Mode** ja lülita režiim sisse.

Ühenda USB-kaabel ja kinnita prillides **Allow USB debugging**. Failidele ligipääsu küsimine on eraldi luba. Kui arendajarežiimi valikut pole, kontrolli kontot ja tiimi liikmesust. Täpsemad, muutuda võivad nõuded on [Meta ametlikus juhendis](https://developers.meta.com/vr/documentation/android-apps/enable-developer-mode/); siinseid samme kontrolliti 01.11.2026.

## 2. Sea ADB valmis

Laadi alla [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools) Windowsile ja paki `platform-tools` kaust näiteks asukohta `C:\Tools\platform-tools`. Paigalda ka [Meta juhendis viidatud Windowsi ADB draiver](https://developers.meta.com/vr/documentation/native/android/mobile-device-setup/).

```bat
set "PATH=C:\Tools\platform-tools;%PATH%"
adb devices -l
```

Questi rea lõpus peab olema `device`. Kui näed `unauthorized`, kinnita USB debugging prillides. Kopeeri rea algusest seadme tunnus ja asenda järgmises käsus `SINU_SEADME_TUNNUS`:

```bat
set "QUEST_SERIAL=SINU_SEADME_TUNNUS"
```

## 3. Salvesta mängus lihtne löök

Ava Elevenis Ball Machine, vali või seadista löök, mida suudad mugavalt tagasi lüüa, ja proovi seda. Salvesta muudatus mängus, välju seadistusvaatest ning sulge Eleven tavaliselt. Nii saab mäng oma seadistused faili kirjutada.

## 4. Ava projekt

Laadi GitHubis **Code → Download ZIP** kaudu projekt alla ja paki lahti. Ava käsuviip selle kaustas. Loo Pythoni keskkond ja paigalda tööriist:

```bat
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m eleven_trainer --help
```

Kui avasid uue käsuviiba, korda selles ka `PATH` ja `QUEST_SERIAL` käske.

## 5. Too seadistused arvutisse ja vali löök

```bat
.venv\Scripts\python -m eleven_trainer pull .local\allikas.json --device "%QUEST_SERIAL%"
.venv\Scripts\python -m eleven_trainer list .local\allikas.json
```

Leia tuttava löögi rida ja kopeeri selle ID. Asenda allpool `SINU_LOOGI_ID`; see on faili tunnus, mitte löögi nimi.

```bat
set "SHOT_ID=SINU_LOOGI_ID"
.venv\Scripts\python -m eleven_trainer build .local\allikas.json .local\esimene.json --shots "%SHOT_ID%" --phases 10 2 --interval 2.8
```

Tulemuses peab olema 12 aktiivset rida: kümme ja seejärel kaks sama lööki. Palli kiirus ja spinn säilivad; `2.8` määrab väljalaskmiste vahe. Algse löögi lisaviivitus säilib.

## 6. Kontrolli ja paigalda

```bat
.venv\Scripts\python -m eleven_trainer install .local\esimene.json --device "%QUEST_SERIAL%" --validate-only
```

Kui kontroll õnnestus, lõpeta käimasolev mäng. Järgmine käsk varundab praeguse faili, asendab Ball Machine'i seadistused ja taaskäivitab Eleveni:

```bat
.venv\Scripts\python -m eleven_trainer install .local\esimene.json --device "%QUEST_SERIAL%"
```

Eduka vastuse olek on `file_verified_after_launch`. Hoia alles vastuses näidatud `original.json` varukoopia.

## 7. Proovi prillides

Ava Ball Machine ja käivita harjutus. Vaata, kas tuttav löök töötab, kas aktiivsed read lähevad järjest ja kas pärast kümmet ning kaht palli algab ring uuesti. Faili edukas kontroll ei tõesta veel mängus toimuvat.

Kahe löögi puhul annaks `--shots ID_A ID_B --phases 10 2` järjekorra **10 A → 10 B → 2 A → 2 B**. Asenda ID-d oma faili tunnustega. Edasi aitavad [eraldi treeningute juhend](../how-to/create-session.md), [Wi-Fi ühendus](../how-to/wifi.md) ja [varukoopia taastamine](../how-to/recover.md). Projekti uus avalik versioon vajab veel eraldi seadmel läbikatsetamist.

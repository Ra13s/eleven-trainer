"""Preview, export, or install a bundled independent experiment."""

import hashlib
from importlib.resources import files
import json

from .device import Adb, install
from .settings import decode, save_new, summary


def catalog():
    return json.loads(files('eleven_trainer.experimental').joinpath('catalog.json').read_text(encoding='utf-8'))['entries']


def load_trial(code, pace='slow'):
    entry = next((item for item in catalog() if item['id'] == code.upper()), None)
    if entry is None:
        raise ValueError('Unknown trial ID; use I01..I12, N01 or R01')
    if pace not in entry['variants']:
        raise ValueError('Unknown pace; use slow, normal or fast')
    entry = {'id': entry['id'], 'name': entry['name'], 'pace': pace, **entry['variants'][pace]}
    payload = files('eleven_trainer.experimental').joinpath(entry['file']).read_bytes()
    if hashlib.sha256(payload).hexdigest() != entry['sha256']:
        raise ValueError('Bundled trial checksum differs; regenerate the complete pack before installing')
    data = decode(payload)
    if summary(data) != {key: entry[key] for key in summary(data)}:
        raise ValueError('Bundled trial metadata differs from the file')
    return entry, payload


def run(args):
    selected = args.id
    if not selected:
        print('INDEPENDENT EXPERIMENTS - R01 is the complete 10/2 cycle.')
        for item in catalog():
            print(f"  {item['id']}  {item['name']} ({item['variants']['slow']['active_rows']} active rows)")
        print('Selecting a trial installs it and restarts Eleven. Q exits. Use --preview for inspection only.')
        selected = input('Trial ID [R01]: ').strip().upper() or 'R01'
        if selected == 'Q':
            return 0
    pace = args.pace
    if pace is None and args.id is None:
        pace = input('Pace: slow (3s), normal (2.4s), fast (1.8s) [slow]: ').strip().lower() or 'slow'
    entry, payload = load_trial(selected, pace or 'slow')
    print(f"\n{entry['id']} - {entry['name']}")
    print(f"Active rows: {entry['active_rows']}; launch interval: {entry['interval_seconds']:g} seconds.")
    print('Experimental: native coordinates, flight and spin behavior have not been calibrated in Eleven.')
    print('Observe launcher side, travel direction, net clearance and landing position.')
    if entry['id'] in ('R01', 'N01'):
        print('Every shot 10 times, then every shot 2 times in the same order. Shuffle OFF.')
    if args.output:
        save_new(args.output, payload)
        print(f'Exported {args.output}; no device contacted')
        return 0
    if args.preview:
        print('Preview only; no device contacted')
        return 0
    device = args.device
    if not device:
        raise ValueError('Installation needs --device SERIAL from the devices command; use --preview to inspect')
    print('Installing with a backup and restarting Eleven...')
    report = install(Adb(args.adb, args.adb_port, device), payload, args.backup_dir)
    print(json.dumps(report, indent=2))
    return 0

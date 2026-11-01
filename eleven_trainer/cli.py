"""Command-line interface; offline commands do not construct an ADB client."""

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .device import Adb, AdbError, install
from .settings import build, decode, encode, load, save_new, summary


def parser():
    root = argparse.ArgumentParser(prog="eleven-trainer", description="Build and install repeatable Eleven ball-machine sessions.")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("list", "validate"):
        command = commands.add_parser(name)
        command.add_argument("source", type=Path)
    command = commands.add_parser("build")
    command.add_argument("source", type=Path)
    command.add_argument("output", type=Path)
    command.add_argument("--shots", nargs="+", help="Shot IDs in desired order; repeats are retained. Default: active rows.")
    command.add_argument("--phases", nargs="+", type=int, default=[10, 2])
    command.add_argument("--interval", type=float, help="Seconds between launches; does not change ball speed.")
    for name in ("devices", "pull", "install"):
        command = commands.add_parser(name)
        command.add_argument("--adb", default="adb", help="ADB executable path")
        command.add_argument("--adb-port", type=int, default=5037)
        if name != "devices":
            command.add_argument("--device", required=True, help="Exact serial or IP:port from adb devices")
        if name == "pull":
            command.add_argument("output", type=Path)
        if name == "install":
            command.add_argument("source", type=Path)
            command.add_argument("--backup-dir", type=Path, default=Path(".local/backups"))
            command.add_argument("--validate-only", action="store_true", help="Run local preflight without contacting ADB")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "list":
            for key, row in load(args.source)["shots"]["data"].items():
                print(f"{key}\tactive={row['isActive']}\t{row['DataName']}")
        elif args.command == "validate":
            print(json.dumps(summary(load(args.source)), indent=2))
        elif args.command == "build":
            result = build(load(args.source), args.shots, args.phases, args.interval)
            save_new(args.output, encode(result))
            print(json.dumps(summary(result), indent=2))
        elif args.command == "install":
            payload = args.source.read_bytes()
            decode(payload)  # Preflight must precede any device access.
            if args.validate_only:
                print("Local installer validation OK; no device contacted")
                return 0
            adb = Adb(args.adb, args.adb_port, args.device)
            print(json.dumps(install(adb, payload, args.backup_dir), indent=2))
        else:
            adb = Adb(args.adb, args.adb_port, getattr(args, "device", None))
            if args.command == "devices":
                print(adb.run("devices", "-l").decode(errors="replace"), end="")
            elif args.command == "pull":
                if args.output.exists():
                    raise FileExistsError(f"Output already exists: {args.output}")
                adb.ready()
                payload = adb.read()
                decode(payload)
                save_new(args.output, payload)
                print(f"Saved {args.output}; the game was not stopped")
        return 0
    except AdbError as exc:
        print(f"Device operation failed: {exc}", file=sys.stderr)
        return 3
    except (OSError, ValueError) as exc:
        print(f"Local file or settings error: {exc}", file=sys.stderr)
        return 2

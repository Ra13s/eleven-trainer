"""Check local Markdown links and parse documented CLI invocations offline."""

from pathlib import Path
import re
import shlex
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from eleven_trainer.cli import parser


def main():
    failures = []
    links = commands = 0
    for path in ROOT.rglob("*.md"):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("mailto:"):
                continue
            relative, _, anchor = unquote(target).partition("#")
            resolved = (path.parent / relative).resolve() if relative else path
            links += 1
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)}: missing {target}")
            elif anchor and resolved.suffix == ".md":
                headings = re.findall(r"^#+\s+(.+)$", resolved.read_text(encoding="utf-8"), re.M)
                slugs = [re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-") for heading in headings]
                if anchor not in slugs:
                    failures.append(f"{path.relative_to(ROOT)}: missing anchor {target}")
        for block in re.findall(r"```[^\n]*\n(.*?)```", text, re.S):
            for line in block.splitlines():
                if " -m eleven_trainer " not in line:
                    continue
                args = line.split(" -m eleven_trainer ", 1)[1]
                if args.strip() in ("--help", "--version"):
                    continue
                try:
                    parser().parse_args(shlex.split(args, posix=False))
                    commands += 1
                except SystemExit as exc:
                    if exc.code:
                        failures.append(f"{path.relative_to(ROOT)}: invalid CLI: {line}")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"PASS: {links} local links/anchors; {commands} documented CLI examples parse")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

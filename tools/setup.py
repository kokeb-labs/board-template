#!/usr/bin/env python3
"""Turn a repository created from board-template into a board (Python 3.9+, PyYAML for the final check).

    python3 tools/setup.py                                  # asks for a title and a description
    python3 tools/setup.py --non-interactive --title "BMP581 breakout" --description "Breakout board for ..."

It infers the organisation and the board name from the repository (`git remote get-url origin`, else the folder
name): `board-bmp581-breakout` in `kokeb-labs-open-boards` is the board `bmp581-breakout`. It fills the placeholders
in board.yml, replaces README.md, AGENTS.md and CHANGELOG.md with the board's own, removes the template tooling
(tools/scaffold and this script) and runs the trace check.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ORG = "kokeb-labs-open-boards"
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def git_remote() -> tuple[str, str] | None:
    """(organisation, repository) from the origin URL, or None."""
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True,
                             check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", url)
    return (m.group(1), m.group(2)) if m else None


def ask(prompt: str, default: str) -> str:
    try:
        answer = input(f"{prompt} [{default}]: ").strip()
    except EOFError:
        answer = ""
    return answer or default


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", help="GitHub organisation (default: from the origin URL)")
    ap.add_argument("--repo", help="repository name (default: from the origin URL, else the folder name)")
    ap.add_argument("--title", help="human title, e.g. 'BMP581 breakout'")
    ap.add_argument("--description", help="one sentence: what the board is")
    ap.add_argument("--non-interactive", action="store_true", help="never ask; missing values take defaults")
    args = ap.parse_args()

    if not (ROOT / "tools" / "scaffold").is_dir():
        print("tools/scaffold is gone: this repository was already set up.", file=sys.stderr)
        return 1

    remote = git_remote()
    org = args.org or (remote[0] if remote else DEFAULT_ORG)
    repo = args.repo or (remote[1] if remote else ROOT.name)
    if not repo.startswith("board-") or len(repo) == len("board-"):
        print(f"The repository name must be board-<name>, not '{repo}'. Rename it first, or pass --repo.",
              file=sys.stderr)
        return 1
    slug = repo[len("board-"):].lower()
    if not SLUG_RE.match(slug):
        print(f"'{slug}' is not a valid board name: use lowercase letters, digits and single hyphens.",
              file=sys.stderr)
        return 1

    interactive = not args.non_interactive and sys.stdin.isatty()
    title = args.title or (ask("Title", slug.replace("-", " ")) if interactive else slug.replace("-", " "))
    default_desc = f"Open Kokeb Labs board: {title}"
    description = args.description or (ask("One-sentence description", default_desc) if interactive else default_desc)

    # board.yml: values go in as JSON strings, which are valid YAML, so quotes and colons are safe.
    board = ROOT / "board.yml"
    text = board.read_text(encoding="utf-8")
    for key, value in (("BOARD", slug), ("TITLE", title), ("DESCRIPTION", description), ("ORG", org),
                       ("REPO", repo)):
        text = text.replace(f'"{{{{{key}}}}}"', json.dumps(value))
    board.write_text(text, encoding="utf-8")

    # The board's own README, AGENTS.md and CHANGELOG replace the template's.
    values = {"{{BOARD}}": slug, "{{TITLE}}": title, "{{DESCRIPTION}}": description, "{{ORG}}": org,
              "{{REPO}}": repo}
    for name in ("README.md", "AGENTS.md", "CHANGELOG.md"):
        body = (ROOT / "tools" / "scaffold" / f"{name}.in").read_text(encoding="utf-8")
        for key, value in values.items():
            body = body.replace(key, value)
        (ROOT / name).write_text(body, encoding="utf-8")

    shutil.rmtree(ROOT / "tools" / "scaffold")
    try:
        Path(__file__).unlink()
    except OSError:
        print("Could not remove tools/setup.py; delete it by hand.")

    print(f"Set up {org}/{repo}: board '{slug}', title '{title}'.")
    sys.path.insert(0, str(ROOT / "tools"))
    import kb_check  # noqa: E402

    print("\nTrace check:")
    code = kb_check.main(["--root", str(ROOT)])
    print("\nNext:")
    print("  1. Replace the example items in trace/ with your own, starting from the needs.")
    print("  2. Put the KiCad project in hardware/ (see hardware/README.md).")
    print("  3. Commit with `git commit -s` and open a pull request.")
    return code


if __name__ == "__main__":
    sys.exit(main())

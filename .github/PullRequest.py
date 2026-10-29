"""Checks a pull request against the gallery's rules. GitHub Actions runs it (.github/workflows/Check.yml):

    OPENED_BY=<GitHub user> ROLE=<author association> python .github/PullRequest.py

BASE is what the pull request is compared with (default HEAD^1: GitHub checks out the pull request merged into its
branch). Every customization must pass Build.py's checks, and these:

- its folder is named after its object's class, and no class name is used twice in the repository;
- its manifest names its author (a GitHub user name) and the MIT license, and the folder holds only its files;
- a new customization's author is whoever opens the pull request;
- a change to one comes from its author, gives it a new "version" and keeps its object's class.

Maintainers (the repository's owners, members and collaborators) may add or change anyone's.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import Build  # noqa: E402

MAINTAINERS = {"OWNER", "MEMBER", "COLLABORATOR"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout


def manifest_at(commit: str, name: str) -> dict | None:
    """A customization's manifest at a commit (None if it wasn't there)."""
    try:
        return json.loads(git("show", f"{commit}:Kits/{name}/manifest.json"))
    except (subprocess.CalledProcessError, ValueError):
        return None


def manifest_now(name: str) -> dict | None:
    path = Build.KITS / name / "manifest.json"
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def object_class(m: dict | None) -> str:
    try:
        return m["object"]["class"]
    except (KeyError, TypeError):
        return ""


def check_every_kit() -> list[str]:
    problems: list[str] = []
    classes: dict[str, str] = {}
    for folder in sorted(p for p in Build.KITS.iterdir() if p.is_dir()):
        where = f"Kits/{folder.name}"
        try:
            Build.build(folder)
        except (Build.KitError, OSError) as e:
            problems.append(f"{where}: {e}")
            continue
        m = manifest_now(folder.name)
        cls = object_class(m)
        if cls != folder.name:
            problems.append(f"{where}: name the folder after its object's class: Kits/{cls}.")
        if m.get("license") != "MIT":
            problems.append(f'{where}: the gallery\'s customizations are MIT licensed, like this repository: set '
                            f'"license": "MIT".')
        if not m.get("author"):
            problems.append(f'{where}: set "author" to your GitHub user name.')
        for name in [cls, *(a.get("class") for a in m.get("animations") or [])]:
            if name in classes:
                problems.append(f"{where}: class {name} is already in Kits/{classes[name]}; choose another name.")
            else:
                classes[name] = folder.name
        extra = sorted(p.name for p in folder.iterdir() if p.name not in Build.FILE_LIMITS)
        if extra:
            problems.append(f"{where}: a customization's folder holds only {', '.join(Build.FILE_LIMITS)}, not "
                            f"{', '.join(extra)}.")
    return problems


def check_changes(base: str, opened_by: str, maintainer: bool) -> tuple[list[str], list[str]]:
    """Problems with what the pull request changes, and the files it changes outside Kits/."""
    changed = [line for line in git("diff", "--name-only", base, "HEAD").splitlines() if line]
    touched = sorted({p.split("/")[1] for p in changed if p.startswith("Kits/") and p.count("/") >= 2})
    outside = [p for p in changed if not p.startswith("Kits/")]
    problems: list[str] = []
    for name in touched:
        where = f"Kits/{name}"
        before, now = manifest_at(base, name), manifest_now(name)
        if before is None:  # a new customization
            if now is not None and now.get("author") != opened_by and not maintainer:
                problems.append(f'{where}: a new customization\'s author is whoever adds it: set "author" to '
                                f'"{opened_by}".')
            continue
        author = before.get("author")
        if opened_by != author and not maintainer:
            problems.append(f"{where}: only its author ({author}) or a maintainer can change or remove it. Open an "
                            "issue to suggest a change.")
        if now is None:  # removed
            continue
        if now.get("author") != author and not maintainer:
            problems.append(f"{where}: its author stays {author}.")
        if (now.get("version") or "1.0") == (before.get("version") or "1.0"):
            problems.append(f'{where}: give it a new "version" (it is "{before.get("version") or "1.0"}"): the gallery '
                            "keeps each version for the projects that use it.")
        if object_class(now) and object_class(now) != object_class(before):
            problems.append(f"{where}: keep its object's class {object_class(before)} (a new folder starts a new "
                            "customization).")
    return problems, outside


def main() -> int:
    base = os.environ.get("BASE") or "HEAD^1"
    opened_by = os.environ.get("OPENED_BY", "")
    maintainer = os.environ.get("ROLE", "") in MAINTAINERS
    problems = check_every_kit()
    changes, outside = check_changes(base, opened_by, maintainer)
    problems += changes
    for problem in problems:
        print(f"::error::{problem}")
    if outside and not maintainer:
        print(f"::notice::This pull request also changes {', '.join(outside[:10])}. A maintainer looks at those "
              "closely.")
    print(f"{len(problems)} problem{'s' if len(problems) != 1 else ''}" if problems else "ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

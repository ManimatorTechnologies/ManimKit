"""Check customizations and zip each into a .manimkit file you can upload to Manimator.

    python Build.py                  -> every folder in Kits/, into Builds/
    python Build.py Kits/Battery     -> just that one

Needs only Python 3.9+ (no packages). It runs the same shape checks Manimator runs on an upload, except one:
Manimator also refuses class names that Manim or Manimator already use (Circle, FadeIn...), and says so on upload.
"""

from __future__ import annotations

import ast
import io
import json
import keyword
import math
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KITS = ROOT / "Kits"
BUILDS = ROOT / "Builds"

FORMAT = 2
SUFFIX = ".manimkit"
MAX_PACKAGE = 1024 * 1024
FILE_LIMITS = {"manifest.json": 64 * 1024, "kit.js": 256 * 1024, "kit.py": 256 * 1024, "README.md": 64 * 1024}
REQUIRED = ("manifest.json", "kit.js", "kit.py")
STYLES = ("none", "shape", "line", "text")
KINDS = ("float", "int", "bool", "color", "str", "text", "direction", "enum", "angle", "point", "vector", "font")
DIRECTIONS = ("UL", "UP", "UR", "LEFT", "ORIGIN", "RIGHT", "DL", "DOWN", "DR")
MAX_PARAMS = 20
MAX_ANIMATIONS = 10
CLASS_RE = re.compile(r"^[A-Z][A-Za-z0-9]{0,39}$")
PARAM_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
AUTHOR_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")  # a GitHub user name
RESERVED_PARAMS = {"mobject", "mobjects", "run_time", "rate_func", "lag_ratio", "name", "self", "args", "kwargs",
                   "target", "dim", "z_index", "introducer", "remover", "suspend_mobject_updating"}
MANIFEST_FIELDS = {"manimkit", "name", "version", "description", "license", "author", "object", "animations"}
OBJECT_FIELDS = {"class", "style", "params"}
ANIMATION_FIELDS = {"class", "name", "description", "params", "introducer", "remover", "run_time"}
PARAM_FIELDS = {"name", "kind", "default", "label", "tooltip", "min", "max", "step", "decimals", "slider", "choices"}
STATIC_IMPORT = re.compile(r"""(?:^|[;\n])\s*(?:import\s*(?:[\w*${}\s,]+?\s*from\s*)?|export\s*[\w*${}\s,]+?\s*from\s*)"""
                           r"""["']([^"'\n]+)["']""")
DYNAMIC_IMPORT = re.compile(r"""\bimport\s*\(""")


class KitError(Exception):
    pass


def _text(value, where: str, most: int, required: bool = False) -> None:
    if value is None and not required:
        return
    if not isinstance(value, str) or (required and not value.strip()):
        raise KitError(f"{where} must be text{' (and not empty)' if required else ''}.")
    if len(" ".join(value.split())) > most:
        raise KitError(f"{where} can be up to {most} characters.")


def _number(value, where: str) -> None:
    if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                              or not math.isfinite(value)):
        raise KitError(f"{where} must be a number.")


def _fields(raw: dict, allowed: set, where: str) -> None:
    unknown = set(raw) - allowed
    if unknown:
        raise KitError(f"{where} has unknown fields {', '.join(sorted(unknown))} (allowed: {', '.join(sorted(allowed))}).")


def _param(raw, where: str) -> str:
    if not isinstance(raw, dict):
        raise KitError(f'{where} must be an object like {{"name": "charge", "kind": "float"}}.')
    _fields(raw, PARAM_FIELDS, where)
    name = raw.get("name")
    if not isinstance(name, str) or not PARAM_RE.match(name) or keyword.iskeyword(name) or name in RESERVED_PARAMS:
        raise KitError(f'{where}.name must be a lowercase Python name (like "charge"), not a keyword or one of '
                       f"{', '.join(sorted(RESERVED_PARAMS))}.")
    kind = raw.get("kind")
    if kind not in KINDS:
        raise KitError(f"{where}.kind must be one of {', '.join(KINDS)}.")
    _text(raw.get("label"), f"{where}.label", 40)
    _text(raw.get("tooltip"), f"{where}.tooltip", 160)
    for field in ("min", "max", "step", "decimals"):
        _number(raw.get(field), f"{where}.{field}")
    if kind in ("float", "int"):
        lo, hi = raw.get("min", -1000), raw.get("max", 1000)
        if not -1e6 <= lo < hi <= 1e6:
            raise KitError(f"{where}: min must be below max (both within ±1000000).")
        if not 0 < raw.get("step", 1 if kind == "int" else 0.1) <= hi - lo:
            raise KitError(f"{where}.step must be positive and fit between min and max.")
        default = raw.get("default")
        if isinstance(default, (int, float)) and not isinstance(default, bool) and not lo <= default <= hi:
            raise KitError(f"{where}.default must be between min and max.")
    choices = raw.get("choices")
    if kind == "enum":
        if not isinstance(choices, list) or not 1 <= len(choices) <= 30 or not all(
                isinstance(c, str) or (isinstance(c, list) and len(c) == 2 and all(isinstance(x, str) for x in c))
                for c in choices):
            raise KitError(f"{where}.choices must list 1 to 30 choices, each text or [value, label].")
    elif kind == "direction" and choices is not None:
        if not isinstance(choices, list) or not choices or any(c not in DIRECTIONS for c in choices):
            raise KitError(f"{where}.choices must be directions: {', '.join(DIRECTIONS)}.")
    elif choices is not None:
        raise KitError(f"{where}: only enum and direction settings have choices.")
    return name


def _params(raw, where: str) -> None:
    params = [] if raw is None else raw
    if not isinstance(params, list) or len(params) > MAX_PARAMS:
        raise KitError(f"{where} must be a list of up to {MAX_PARAMS} settings.")
    names = [_param(p, f"{where}[{i}]") for i, p in enumerate(params)]
    if len(set(names)) != len(names):
        raise KitError(f"two settings in {where} have the same name.")


def _class(value, where: str, taken: set) -> str:
    if not isinstance(value, str) or not CLASS_RE.match(value):
        raise KitError(f'{where} must be a PascalCase class name, like "Battery".')
    if value in taken:
        raise KitError(f'{where}: "{value}" is used twice in this customization.')
    taken.add(value)
    return value


def check_manifest(text: str) -> list[str]:
    """manifest.json checked; returns every class name, the object's first."""
    try:
        raw = json.loads(text)
    except ValueError as e:
        raise KitError(f"manifest.json isn't valid JSON ({e}).") from None
    if not isinstance(raw, dict):
        raise KitError("manifest.json must be a JSON object.")
    if raw.get("manimkit") != FORMAT:
        raise KitError(f'"manimkit" must be {FORMAT}.')
    _fields(raw, MANIFEST_FIELDS, "manifest.json")
    _text(raw.get("name"), "name", 40, required=True)
    _text(raw.get("version"), "version", 20)
    _text(raw.get("description"), "description", 200)
    _text(raw.get("license"), "license", 60)
    _text(raw.get("author"), "author", 39)
    if raw.get("author") is not None and not AUTHOR_RE.match(raw["author"]):
        raise KitError('author must be your GitHub user name, like "SavithOnline".')
    obj = raw.get("object")
    if not isinstance(obj, dict):
        raise KitError('give the "object": {"class": "Battery", "params": [...]}.')
    _fields(obj, OBJECT_FIELDS, "object")
    taken: set = set()
    classes = [_class(obj.get("class"), "object.class", taken)]
    if obj.get("style", "none") not in STYLES:
        raise KitError(f'object.style must be one of {", ".join(STYLES)}.')
    _params(obj.get("params"), "object.params")
    animations = raw.get("animations") or []
    if not isinstance(animations, list) or len(animations) > MAX_ANIMATIONS:
        raise KitError(f'"animations" must be a list of up to {MAX_ANIMATIONS} animations.')
    for i, a in enumerate(animations):
        where = f"animations[{i}]"
        if not isinstance(a, dict):
            raise KitError(f'{where} must be an object like {{"class": "PopIn", "params": []}}.')
        _fields(a, ANIMATION_FIELDS, where)
        classes.append(_class(a.get("class"), f"{where}.class", taken))
        _text(a.get("name"), f"{where}.name", 40)
        _text(a.get("description"), f"{where}.description", 200)
        _params(a.get("params"), f"{where}.params")
        if a.get("introducer") and a.get("remover"):
            raise KitError(f"{where}: an animation can't both bring in and take away its object.")
        _number(a.get("run_time"), f"{where}.run_time")
        if not 0.05 <= a.get("run_time", 1.0) <= 60:
            raise KitError(f"{where}.run_time must be between 0.05 and 60 seconds.")
    return classes


def check_python(source: str, classes: list[str]) -> None:
    try:
        tree = ast.parse(source, filename="kit.py")
    except SyntaxError as e:
        raise KitError(f"kit.py has a syntax error on line {e.lineno}: {e.msg}.") from None
    defined = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
    for cls in classes:
        if cls not in defined:
            raise KitError(f"kit.py must define class {cls} at the top level (manifest.json names it).")


def check_javascript(source: str, classes: list[str]) -> None:
    for spec in STATIC_IMPORT.findall(source):
        if spec != "manimator":
            raise KitError(f'kit.js imports {spec[:60]!r}: it may import only from "manimator".')
    if DYNAMIC_IMPORT.search(source):
        raise KitError('kit.js can\'t use import(): it may import only from "manimator".')
    for cls in classes:
        if not re.search(rf"\bexport\s+class\s+{cls}\b|\bexport\s*{{[^}}]*\b{cls}\b[^}}]*}}", source):
            raise KitError(f"kit.js must export class {cls} by its name: `export class {cls} extends ...`.")


def build(folder: Path) -> bytes:
    """The folder checked and zipped as a .manimkit file."""
    files = {}
    for name, limit in FILE_LIMITS.items():
        path = folder / name
        if path.is_file():
            text = path.read_text(encoding="utf-8-sig")
            if len(text.encode("utf-8")) > limit:
                raise KitError(f"{name} is too large (up to {limit // 1024} KB).")
            files[name] = text
    missing = [r for r in REQUIRED if r not in files]
    if missing:
        raise KitError(f"missing {', '.join(missing)}.")
    classes = check_manifest(files["manifest.json"])
    check_python(files["kit.py"], classes)
    check_javascript(files["kit.js"], classes)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            z.writestr(name, text)
    data = buf.getvalue()
    if len(data) > MAX_PACKAGE:
        raise KitError(f"the {SUFFIX} file can be up to {MAX_PACKAGE // 1024} KB.")
    return data


def main(args: list[str]) -> int:
    if any(a.startswith("-") for a in args):
        print(__doc__)
        return 0
    folders = [Path(a) for a in args] or sorted(p for p in KITS.iterdir() if p.is_dir())
    failed = 0
    BUILDS.mkdir(exist_ok=True)
    for folder in folders:
        try:
            data = build(folder)
        except (KitError, OSError) as e:
            print(f"{folder.name}: {e}")
            failed += 1
            continue
        target = BUILDS / f"{folder.name}{SUFFIX}"
        target.write_bytes(data)
        print(f"{folder.name}: ok -> {target.relative_to(ROOT)} ({len(data)} bytes)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Check libraries as Manimator checks them when this repository changes.

    python Build.py                      -> every folder in Libraries/
    python Build.py Libraries/ManimChem  -> just that one

Needs only Python 3.9+ (no packages). It runs the shape checks Manimator runs; Manimator checks the settings in more
detail, and refuses class names Manim, Manimator or another library already use (Circle, FadeIn...).
"""

from __future__ import annotations

import ast
import json
import keyword
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIBRARIES = ROOT / "Libraries"

FORMAT = 3
MAX_UNPACKED = 12 * 1024 * 1024
MAX_FILE = 2 * 1024 * 1024
MAX_FILES = 400
TOP_FILES = {"manifest.json": 64 * 1024, "README.md": 64 * 1024, "LICENSE": 64 * 1024, "LICENSE.md": 64 * 1024,
             "LICENSE.txt": 64 * 1024}
PACKAGE_SUFFIXES = (".py", ".csv", ".tsv", ".json", ".txt", ".md", ".mol", ".sdf", ".xml", ".dat")
MANIFEST_FIELDS = {"manimkit", "name", "category", "version", "description", "license", "author", "library", "objects",
                   "animations"}
OBJECT_FIELDS = {"class", "name", "description", "style", "params"}
ANIMATION_FIELDS = {"class", "name", "description", "params", "introducer", "remover", "run_time", "only"}
PARAM_FIELDS = {"name", "kind", "default", "label", "tooltip", "min", "max", "step", "decimals", "slider", "choices"}
KINDS = ("float", "int", "bool", "color", "str", "text", "direction", "enum", "angle", "point", "vector", "font")
STYLES = ("none", "shape", "line", "text")
MAX_PARAMS = 20
MAX_CLASSES = 20
CLASS_RE = re.compile(r"^[A-Z][A-Za-z0-9]{0,39}$")
PARAM_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,39}$")
PART_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,99}$")
AUTHOR_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")  # a GitHub user name
RESERVED_PARAMS = {"mobject", "mobjects", "run_time", "rate_func", "lag_ratio", "name", "self", "args", "kwargs",
                   "target", "dim", "z_index", "introducer", "remover", "suspend_mobject_updating"}
PYODIDE_PACKAGES = ("biopython", "mpmath", "networkx", "pandas", "pillow", "pyyaml", "regex", "scipy", "shapely", "sympy")
RESERVED_PACKAGES = {"manim", "manimlib", "customizations", "numpy", "np", "js", "pyodide", "pyodide_js", "micropip",
                     "_manimator", "scene", "networkx", "pandas", "scipy", "sympy", "mpmath", "PIL", "yaml", "regex",
                     "shapely", "Bio", "pytest", "setuptools", "pip"}
# the names of the Python download's own files and folders, which sit next to the package folders (compared ignoring
# case, as Windows and macOS do)
LAYOUT_NAMES = {"scenes", "assets", "fonts", "codeview", "readme", "requirements"}


class KitError(ValueError):
    pass


def _fields(raw: dict, allowed: set, where: str) -> None:
    unknown = set(raw) - allowed
    if unknown:
        raise KitError(f"manifest.json: {where}unknown fields {', '.join(sorted(unknown))}.")


def _text(value, where: str, most: int, required: bool = False) -> None:
    if value is None and not required:
        return
    if not isinstance(value, str) or (required and not value.strip()):
        raise KitError(f"manifest.json: give {where} as text.")
    if len(value) > most:
        raise KitError(f"manifest.json: {where} can be up to {most} characters.")


def _params(raw, where: str) -> None:
    if raw is None:
        return
    if not isinstance(raw, list) or len(raw) > MAX_PARAMS:
        raise KitError(f"manifest.json: {where} must be a list of up to {MAX_PARAMS} settings.")
    names = set()
    for i, p in enumerate(raw):
        at = f"{where}[{i}]"
        if not isinstance(p, dict):
            raise KitError(f"manifest.json: {at} must be an object.")
        _fields(p, PARAM_FIELDS, f"{at}: ")
        name = p.get("name")
        if not isinstance(name, str) or not PARAM_RE.match(name) or keyword.iskeyword(name) or name in RESERVED_PARAMS:
            raise KitError(f"manifest.json: {at}.name must be a lowercase Python name, not a keyword or one of "
                           f"{', '.join(sorted(RESERVED_PARAMS))}.")
        if name in names:
            raise KitError(f"manifest.json: {at}.name {name!r} is used twice.")
        names.add(name)
        if p.get("kind") not in KINDS:
            raise KitError(f"manifest.json: {at}.kind must be one of {', '.join(KINDS)}.")


def check_manifest(text: str) -> tuple[str, list[str]]:
    """manifest.json, checked as Manimator checks it. Returns (package name, every class it offers)."""
    try:
        raw = json.loads(text)
    except ValueError as e:
        raise KitError(f"manifest.json isn't valid JSON ({e}).") from None
    if not isinstance(raw, dict) or raw.get("manimkit") != FORMAT or not isinstance(raw.get("library"), dict):
        raise KitError(f'manifest.json: "manimkit" must be {FORMAT}, with "library": {{"package": ...}}.')
    _fields(raw, MANIFEST_FIELDS, "")
    _text(raw.get("name"), "name", 40, required=True)
    _text(raw.get("category"), "category", 24)
    _text(raw.get("version"), "version", 20)
    _text(raw.get("description"), "description", 200)
    if len(str(raw.get("description") or "").split()) > 25:
        raise KitError("manifest.json: description can be up to 25 words.")
    _text(raw.get("license"), "license", 60)
    author = raw.get("author")
    if author is not None and (not isinstance(author, str) or not AUTHOR_RE.match(author)):
        raise KitError('manifest.json: author must be a GitHub user name, like "SavithOnline".')
    lib = raw["library"]
    _fields(lib, {"package", "requires"}, "library: ")
    package = lib.get("package")
    if not isinstance(package, str) or not PACKAGE_RE.match(package) or keyword.iskeyword(package):
        raise KitError('manifest.json: library.package must be the name scripts import it by, like "manimchem".')
    if (package in RESERVED_PACKAGES or package in getattr(sys, "stdlib_module_names", ())
            or package.lower() in LAYOUT_NAMES):
        raise KitError(f"manifest.json: library.package can't be {package!r}: Python or Manimator uses that name.")
    requires = lib.get("requires") or []
    if not isinstance(requires, list) or len(requires) > 10 or not all(r in PYODIDE_PACKAGES for r in requires):
        raise KitError(f"manifest.json: library.requires can name only {', '.join(PYODIDE_PACKAGES)}.")
    classes: list[str] = []
    objects = raw.get("objects") or []
    animations = raw.get("animations") or []
    for key, items, fields in (("objects", objects, OBJECT_FIELDS), ("animations", animations, ANIMATION_FIELDS)):
        if not isinstance(items, list) or len(items) > MAX_CLASSES:
            raise KitError(f'manifest.json: "{key}" must be a list of up to {MAX_CLASSES}.')
        for i, item in enumerate(items):
            where = f"{key}[{i}]"
            if not isinstance(item, dict):
                raise KitError(f"manifest.json: {where} must be an object.")
            _fields(item, fields, f"{where}: ")
            cls = item.get("class")
            if not isinstance(cls, str) or not CLASS_RE.match(cls) or cls in classes:
                raise KitError(f"manifest.json: {where}.class must be a PascalCase class name, used once.")
            classes.append(cls)
            if item.get("style", "none") not in STYLES:
                raise KitError(f"manifest.json: {where}.style must be one of {', '.join(STYLES)}.")
            _params(item.get("params"), f"{where}.params")
            if key == "animations":
                if item.get("introducer") and item.get("remover"):
                    raise KitError(f"manifest.json: {where} can't both bring in and take away its object.")
                only = item.get("only") or []
                if not isinstance(only, list) or any(c not in [o.get("class") for o in objects] for c in only):
                    raise KitError(f'manifest.json: {where}.only must list classes from "objects".')
    if not classes:
        raise KitError('manifest.json: list at least one class in "objects" or "animations": the editor uses a '
                       "library through them.")
    return package, classes


def check(folder: Path) -> None:
    """A library's folder, checked as Manimator checks it: manifest.json, README.md, its license and its package folder
    (Python and text data files; every .py must parse and the package must define each class the manifest offers)."""
    manifest = folder / "manifest.json"
    if not manifest.is_file():
        raise KitError("missing manifest.json.")
    package, classes = check_manifest(manifest.read_text(encoding="utf-8-sig"))
    if not (folder / package / "__init__.py").is_file():
        raise KitError(f"the library needs its package folder {package}/ with {package}/__init__.py.")
    defined: set[str] = set()
    total = files = 0
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder).as_posix()
        parts = rel.split("/")
        if path.is_dir() or "__pycache__" in parts or path.suffix == ".pyc":
            continue
        if any(not PART_RE.match(p) or p.startswith(".") for p in parts):
            raise KitError(f"unexpected file {rel}: use plain file and folder names.")
        if len(parts) == 1 and rel not in TOP_FILES:
            raise KitError(f"unexpected file {rel}: next to manifest.json a library holds only {package}/, "
                           "README.md and its license.")
        if len(parts) > 1 and (parts[0] != package or not rel.lower().endswith(PACKAGE_SUFFIXES)):
            raise KitError(f"unexpected file {rel}: a library holds Python and text data files in {package}/.")
        text = path.read_text(encoding="utf-8-sig")
        size = len(text.encode("utf-8"))
        limit = TOP_FILES.get(rel, MAX_FILE)
        total += size
        files += 1
        if size > limit or total > MAX_UNPACKED:
            raise KitError(f"{rel} is too large (up to {limit // 1024} KB), or the library is.")
        if rel.endswith(".py"):
            try:
                tree = ast.parse(text, filename=rel)
            except SyntaxError as e:
                raise KitError(f"{rel} has a syntax error on line {e.lineno}: {e.msg}.") from None
            defined |= {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    if files > MAX_FILES:
        raise KitError(f"a library holds up to {MAX_FILES} files.")
    missing = [c for c in classes if c not in defined]
    if missing:
        raise KitError(f"the package must define class {missing[0]} (manifest.json offers it to the editor).")


def main(args: list[str]) -> int:
    if any(a.startswith("-") for a in args):
        print(__doc__)
        return 0
    folders = [Path(a) for a in args] or sorted(p for p in LIBRARIES.iterdir() if p.is_dir())
    failed = 0
    for folder in folders:
        try:
            check(folder)
        except (KitError, OSError, UnicodeDecodeError) as e:
            print(f"{folder.name}: {e}")
            failed += 1
            continue
        print(f"{folder.name}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# AGENTS.md

This repo is for writing Manimator libraries. Each library is a Python package written in plain Manim Community, and
every library here is in everyone's Manimator. Manimator runs it in the user's browser (Pyodide, on Manimator's own
`manim` module, which draws with its engine): the visual editor offers the classes its manifest lists, objects in a
palette group of their own (its `category`) and animations in a group of the animation list. That is the only way
Manimator uses a library. People who want to program download the
project as Python: the package goes next to `Scenes.py`, which imports it by name (`from manimchem import BohrAtom`),
and real Manim runs it. Write it once, in Python.

## Layout

```
Libraries/<Name>/manifest.json   names, the package, the objects and animations the editor offers, their settings
Libraries/<Name>/<package>/      the package: __init__.py, more .py files, text data files
Libraries/<Name>/Icons/<Class>.svg  optional: an object's picture in the palette (up to 32 KB, 96x96 viewBox)
Libraries/<Name>/README.md       shown to users
Libraries/<Name>/LICENSE.md      its license (goes into downloads with it)
Build.py                         checks a library as Manimator does
.github/PullRequest.py           the repository's extra rules, checked on every pull request
```

Name folders in PascalCase after the package (`Libraries/ManimChem` for `manimchem`).

## Workflow

1. Start from `Libraries/ManimChem` (many objects, animations written in Python, data files, PubChem).
2. Write the package and try it in Manim on a computer: put a small `Scenes.py` that imports it next to the package
   folder, as the Python download does, and run `manim -pql Scenes.py MyScene`.
3. List in `manifest.json` the classes the editor should offer, with their settings.
4. Run `python Build.py Libraries/<Name>`. Fix every error it prints. Exit code 0 means it passed.
5. The user tries it in Manimator run on their computer, pointed at their fork's branch (CONTRIBUTING.md). Only
   Manimator shows how it draws.
6. The user opens a pull request to this repository (CONTRIBUTING.md). Once merged, it is in everyone's Manimator:
   each later change to the folder becomes a new version.

## manifest.json

```json
{
  "manimkit": 3,
  "name": "manimchem",
  "version": "0.7.0",
  "description": "Chemistry for Manim",
  "license": "MIT",
  "author": "SavithOnline",
  "library": {"package": "manimchem", "requires": []},
  "objects": [
    {"class": "BohrAtom", "name": "Bohr atom", "description": "Electrons on their shells",
     "params": [{"name": "e", "kind": "int", "default": 6, "min": 1, "max": 118, "label": "Electrons"}]}
  ],
  "animations": [
    {"class": "OrbitElectrons", "name": "Orbit electrons", "only": ["BohrAtom"], "run_time": 3,
     "params": [{"name": "turns", "kind": "float", "default": 1, "label": "Turns"}]}
  ]
}
```

- `manimkit` is always `3`. `name` is required (up to 40 chars), `description` up to 25 words. `category`: its
  group in the palette and the animation list, up to 24 chars (`"Chemistry"`); the name if left out.
- `author` is the GitHub user name of whoever wrote it. `license` is `"MIT"` for everything in this repository.
- `library.package`: the import name. Not a name Python, Manim or Manimator uses (`os`, `numpy`, `manim`...), nor,
  ignoring case, a name the Python download gives its own files and folders: `scenes`, `assets`, `fonts`,
  `codeview`, `readme`, `requirements`. `library.requires`: only Pyodide's packages: biopython, mpmath, networkx,
  pandas, pillow, pyyaml, regex, scipy, shapely, sympy.
- List at least one class in `objects` or `animations`: Manimator uses a library only through them.
- `objects` (up to 20): `class` (PascalCase, defined in the package, not one of Manim's names), `name` and
  `description` for the editor, `style` (`"none"`: its own colors; `"shape"`, `"line"` or `"text"`: the editor's color
  controls), `params`.
- `animations` (up to 20): `class`, `name`, `description`, `params`, `run_time` (0.05 to 60 s),
  `"introducer": true` (brings its object in, like FadeIn) or `"remover": true` (takes it away), and `only`: the
  object classes it plays on (leave it out to play on any object).
- `params` (up to 20 per class): the editor calls the class with every one of them, by name, at their manifest
  defaults unless the user changes them (so the class's own defaults don't matter there). Names are lowercase Python
  names, and can't be `name`, `mobject`, `run_time`, `rate_func`, `lag_ratio`, `target`, `dim`, `z_index`,
  `introducer` or `remover`. Kinds: `float` and `int` (with `min`, `max`, `step`, `decimals`, `slider`), `bool`,
  `color` (`"#RRGGBB"`), `str`, `text`, `font`, `angle` (degrees in the manifest, radians in your code), `point` and
  `vector` (`[x, y]`), `direction` (`"UP"`, `"DL"`...), `enum` (`choices`: text, or `[value, label]`). Every param can
  have `default`, `label` (up to 40 chars) and `tooltip` (up to 160).
- A new version must keep the package name; objects, animations and settings may change.

## The package

- Plain Manim Community: `from manim import *`. It must run in Manim on a computer too.
- What works in Manimator: subclasses of Manim's objects and animations, with their own methods, `super()` calls and
  attributes (also on copies); animations with their own `interpolate_mobject` / `interpolate_submobject`; Manim
  classes passed to Manim (a Graph's `edge_type`); 3D with `Sphere`, `Line3D` and `Surface` in a `ThreeDScene`.
- Not: OpenGL classes, and overriding Manim's private methods (names starting with `_`) to change its data
  structures: Manimator's engine keeps its own. Use Manim's public options.
- Editor classes take plain settings (numbers, text, colors...). Give each a constructor whose keyword arguments are
  the manifest's params (for example `Molecule2D(pubchem="caffeine", style="graph")`).
- Data files: next to the modules, read with `Path(__file__).parent`. Users can't upload data files to Manimator:
  take a user's data as a setting (a `text` param, like manimchem's `.mol` text). The only website a package may
  read is PubChem's REST API, with a synchronous request: `js.XMLHttpRequest` in the browser
  (`sys.platform == "emscripten"`), `urllib` elsewhere.
- Keep randomness seeded (a `seed` setting): the editor builds objects again and again, and should get the same one.
- Only Python and text data files (.py .csv .tsv .json .txt .md .mol .sdf .xml .dat), plain names, up to 2 MB each,
  12 MB in all. Every .py must parse; Manimator never runs it on its server.

## The repository's rules

Pull requests are checked by `.github/PullRequest.py` (and read by a maintainer before merging): the folder is
named after its package; no package or class name is used by another folder; `author` is set (for a new one, the
GitHub user opening the pull request) and `license` is `"MIT"`; a change needs its author or a maintainer, a new
`version`, and the same package name; one library per pull request.

## Reference

- Full guide: <https://manimator.app/docs/libraries>
- `Libraries/ManimChem` is a working, live example. When unsure how to do something, copy what it does.

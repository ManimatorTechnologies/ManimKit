# ManimKit

Write **libraries** for [Manimator](https://manimator.app): Python packages written in Manim. Every library in this
repository is in everyone's Manimator, with nothing to add: its objects get their own group in the visual editor's
palette, and its animations their own group in the animation list. They run in the user's browser, in Python. The
project's **Download** puts the package next to `Scenes.py` (`from manimchem import BohrAtom`), so the same scenes
render in Manim Community on a computer.

Every folder in `Libraries/` is one library. `Build.py` checks a library the way Manimator does.

## Quick start

1. Fork this repo.
2. Make a folder in `Libraries/`, named after your package: `Libraries/Pendulums` for `pendulums`.
3. Put your package in it (`Libraries/Pendulums/pendulums/__init__.py` and more), with a `manifest.json` and a
   `README.md` (see below).
4. Run `python Build.py Libraries/Pendulums` (Python 3.9+, nothing to install) and fix what it prints.
5. Try it in Manimator on your own computer (see [CONTRIBUTING.md](CONTRIBUTING.md)), then open a pull request.

Running `python Build.py` on its own checks every folder in `Libraries/`.

## What's in a library

| File | What it is |
|---|---|
| `manifest.json` | Its name, its palette group (`category`), its package, and the objects and animations the editor offers (at least one), with their settings |
| `<package>/` | The Python package, written in plain Manim, and the text data files it reads |
| `Icons/` | Optional: `<Class>.svg` for each object, its picture in the editor's palette (its symbol if none) |
| `README.md` | How to use it |
| `LICENSE.md` | Its license, which goes into downloads with it |

## The libraries

| Library | What it has |
|---|---|
| [ManimChem](Libraries/ManimChem) | `manimchem`: molecules in 2D and 3D (from PubChem or .mol files), Bohr atoms, orbitals, element cards, periodic tables and formulas. A fork of [manim-chemistry](https://github.com/UnMolDeQuimica/manim-Chemistry) |

## Learn more

- [AGENTS.md](AGENTS.md) has the full rules. It's written for AI coding agents, but people can read it too.
- The Libraries guide in Manimator's docs: <https://manimator.app/docs/libraries>

## License

MIT. See [LICENSE](LICENSE). Every library here is MIT too.

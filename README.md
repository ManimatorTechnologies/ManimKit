# ManimKit

Write **customizations** for [Manimator](https://manimator.app): Python libraries written in Manim. Once a user adds
one, its objects and animations appear in Manimator's visual editor, and its package can be imported in the Code
view (`from manimchem import *`). Both run in the user's browser, in Python. The Python download puts the package next
to `scene.py`, so the same scene renders in Manim on a computer.

This repo is also Manimator's **gallery**: every folder in `Libraries/` is a customization anyone can add. It has a
script that checks a customization and packs it into a `.manimkit` file ready to upload.

## Quick start

1. Fork or copy this repo.
2. Make a folder in `Libraries/`, named after your package: `Libraries/Pendulums` for `pendulums`.
3. Put your package in it (`Libraries/Pendulums/pendulums/__init__.py` and more), with a `manifest.json` and a
   `README.md` (see below).
4. Run `python Build.py Libraries/Pendulums` (Python 3.9+, nothing to install). It checks the files and writes
   `Builds/Pendulums.manimkit`.
5. In Manimator, open **Customizations**, upload the file, and try its objects in the editor and its package in the
   Code view.
6. To share it in the gallery, open a pull request: see [CONTRIBUTING.md](CONTRIBUTING.md).

Running `python Build.py` on its own builds every folder in `Libraries/`.

## What's in a customization

| File | What it is |
|---|---|
| `manifest.json` | Its name, its package, and the objects and animations the editor offers, with their settings |
| `<package>/` | The Python package, written in plain Manim, and the text data files it reads |
| `README.md` | How to use it, shown on its page |
| `LICENSE.md` | Its license, which goes into downloads with it |

## In the gallery

| Customization | What it has |
|---|---|
| [ManimChem](Libraries/ManimChem) | `manimchem`: molecules in 2D and 3D (from PubChem or .mol files), Bohr atoms, orbitals, element cards, periodic tables and formulas. A fork of [manim-chemistry](https://github.com/UnMolDeQuimica/manim-Chemistry) |

## Learn more

- [AGENTS.md](AGENTS.md) has the full rules. It's written for AI coding agents, but people can read it too.
- The Customizations guide in Manimator's docs: <https://manimator.app/docs/customizations>

## License

MIT. See [LICENSE](LICENSE). The gallery's customizations are MIT too. One you only upload to your own
Customizations can use any license; set it in `manifest.json`.

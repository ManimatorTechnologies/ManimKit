# manimchem

Chemistry for Manim: molecules in 2D and 3D, atomic orbitals, Bohr diagrams, element cards, periodic tables and
chemical formulas. In [Manimator](https://manimator.app) its objects and animations are in the editor, running in your
browser. It runs in Manim Community on your computer too, for example from Manimator's Python download.

```python
from manim import *
from manimchem import *


class Caffeine(Scene):
    def construct(self):
        molecule = MMoleculeObject.molecule_from_pubchem(name="caffeine")
        self.play(Write(molecule))
```

manimchem is a fork of [manim-chemistry](https://github.com/UnMolDeQuimica/manim-Chemistry) by UMDQ (MIT). Its
[original guide](https://github.com/UnMolDeQuimica/manim-Chemistry#readme) still describes most of what it does; use
`manimchem` where it says `manim_chemistry`.

## What changed from manim-chemistry

- **Import it as `manimchem`.**
- **3D needs no OpenGL.** `ThreeDMolecule`, `ThreeDAtom`, `ThreeDBond` and `Orbital` are made of Manim's usual
  `Sphere`, `Line3D` and `Surface`. Draw them in a `ThreeDScene` and turn the camera with `set_camera_orientation`.
- **The element table comes with it.** `PeriodicTable()`, `MElementObject.from_csv_file_data(atomic_number=6)` and
  `ThreeDMolecule` work without a CSV file. You can still pass your own file.
- **Fewer packages.** It needs only `manim` and `numpy` (`click` for its command line). pandas, scipy, requests,
  xmltodict and networkx are gone. Orbitals use their own spherical harmonics, which match scipy's.
- **PubChem works in the browser.** `molecule_from_pubchem` uses the browser's own request in Manimator, and Python's
  `urllib` elsewhere.
- **`GraphMolecule` uses Manim's public `edge_type`.** Each bond is a `BondEdge` holding a `SimpleLine`,
  `DoubleLine` or `TripleLine`. It no longer overrides Graph's internal `_populate_edge_dict`.

## In Manimator

It is in everyone's Manimator, with nothing to add:

- **In the editor**, the palette's Chemistry group has Molecule (from PubChem by name, or pasted .mol text; drawn as a
  structural formula or as atoms and bonds), 3D molecule, Bohr atom, Orbital, Element card, Periodic table and
  Formula, and the animation list has Spin and Orbit electrons (for Bohr atoms).
- **To program**, download the project (**Download**, or File → Download, Ctrl+S): a ZIP of Python. It
  has the `manimchem` folder next to `Scenes.py`, which imports it (`from manimchem import BohrAtom`), so the scenes
  render with Manim Community: `manim -pqh Scenes.py MyScene`. There `molecule_from_file` reads your own .mol and
  .sdf files, and `molecule_from_pubchem` reads PubChem.

## Classes

| Class | What it draws |
| --- | --- |
| `MMoleculeObject` | A 2D structural formula, from a file (`molecule_from_file`), text or PubChem |
| `NamedMolecule` | A 2D molecule with its name under it |
| `GraphMolecule` | A molecule as a Manim `Graph`: atoms are dots, bonds lines |
| `ThreeDMolecule` | A 3D ball-and-stick molecule |
| `Orbital` | An atomic orbital's shape, from `l` and `m` |
| `BohrAtom` | A Bohr diagram, from electrons `e`, protons `p` and neutrons `n` |
| `MElementObject` | One element's card |
| `PeriodicTable` | The periodic table |
| `ChemicalFormula`, `NamedFormula` | Formulas with subscripts, with or without names |
| `Molecule2D`, `Molecule3D`, `ElementCard` | The editor's molecules and element card: they take plain settings |
| `Spin`, `OrbitElectrons` | Animations: turn an object, move a Bohr atom's electrons around |

## License

MIT. Copyright (c) 2023 UMDQ, and (c) 2026 Savith Enterprise for the changes. See LICENSE.md.

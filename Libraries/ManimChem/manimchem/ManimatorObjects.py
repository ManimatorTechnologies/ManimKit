"""Objects and animations that take plain settings: Manimator's visual editor builds these (its manifest.json lists
them), and they are handy in code too.

    Molecule2D(pubchem="caffeine")               a structural formula (or a graph) from PubChem, or from .mol text
    Molecule3D(pubchem="caffeine")               a ball-and-stick molecule, from PubChem's 3D record or .mol text
    ElementCard(atomic_number=6)                 one element's card
    Spin(mobject, turns=1)                       turns an object about its center
    OrbitElectrons(bohr_atom, turns=1)           moves a BohrAtom's electrons around their shells
"""

import numpy as np

from manim import TAU, Animation, VGroup

from .bohr_atom.bohr_atom import BohrAtom
from .periodic_table.table_objects import MElementObject
from .threeD.threedmolecule import ThreeDMolecule
from .twoD.graph_molecule import GraphMolecule
from .twoD.molecule import MMoleculeObject

__all__ = ["Molecule2D", "Molecule3D", "ElementCard", "Spin", "OrbitElectrons"]


def _molecule(cls, pubchem: str, mol: str, three_d: bool = False, **kwargs):
    """A molecule of `cls` from .mol text when there is some, else from PubChem by name."""
    if str(mol).strip():
        return cls.molecule_from_string(str(mol), format="mol", **kwargs)
    return cls.molecule_from_pubchem(name=str(pubchem).strip() or "water", three_d=three_d, **kwargs)


class Molecule2D(VGroup):
    """A molecule drawn flat: as a structural formula (style "structural") or as a graph of atoms and bonds
    (style "graph"). It comes from PubChem by name (`pubchem`), or from the text of a .mol file (`mol`)."""

    def __init__(self, pubchem="caffeine", mol="", style="structural", hydrogens=False, numbers=False, **kwargs):
        super().__init__(**kwargs)
        self.pubchem = pubchem
        self.style = style
        if style == "graph":
            self.molecule = _molecule(GraphMolecule, pubchem, mol, ignore_hydrogens=not hydrogens,
                                      numeric_label=bool(numbers))
        else:
            self.molecule = _molecule(MMoleculeObject, pubchem, mol, ignore_hydrogens=not hydrogens,
                                      explicit_hydrogens=bool(hydrogens), straighten=True,
                                      add_atoms_numbering=bool(numbers))
        self.add(self.molecule)


class Molecule3D(VGroup):
    """A ball-and-stick molecule, from PubChem's 3D record by name (`pubchem`) or from the text of a .mol file (`mol`).
    Show it in a 3D scene and turn the camera to see it in depth."""

    def __init__(self, pubchem="caffeine", mol="", hydrogens=True, **kwargs):
        super().__init__(**kwargs)
        self.pubchem = pubchem
        self.molecule = _molecule(ThreeDMolecule, pubchem, mol, three_d=True, ignore_hydrogens=not hydrogens)
        self.add(self.molecule)


class ElementCard(VGroup):
    """One element's card from the periodic table: its number, symbol, name and color."""

    def __init__(self, atomic_number=6, **kwargs):
        super().__init__(**kwargs)
        self.atomic_number = max(1, min(118, int(atomic_number)))
        self.add(MElementObject.from_csv_file_data(atomic_number=self.atomic_number))


class Spin(Animation):
    """Turns its object about its center, `turns` times."""

    def __init__(self, mobject, turns=1.0, **kwargs):
        self.turns = turns
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        self.mobject.become(self.starting_mobject)
        self.mobject.rotate(self.rate_func(alpha) * TAU * self.turns)


class OrbitElectrons(Animation):
    """Moves a BohrAtom's electrons around their shells, `turns` times for the innermost (outer shells go slower)."""

    def __init__(self, mobject, turns=1.0, **kwargs):
        self.turns = turns
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        self.mobject.become(self.starting_mobject)
        center = np.array(self.mobject.get_center())
        for i, shell in enumerate(self.mobject[1]):
            shell.rotate(self.rate_func(alpha) * TAU * self.turns / (i + 1), about_point=center)

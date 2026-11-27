import numpy as np

from manim import Line3D, VGroup


class ThreeDBond(VGroup):
    """
    Used to create a tridimensional bond.
    Uses an origin atom and a target atom to be drawn: each half of the bond has its atom's color.

    Works with Manim's usual (Cairo) renderer: draw it in a ThreeDScene.
    """

    def __str__(self):
        return f"ThreeDBond bonding {self.from_atom} with {self.to_atom}"

    def __repr__(self):
        return self.__str__()

    def __init__(
        self,
        from_atom,
        to_atom,
        bond_type=1,
        *mobjects,
        thickness: float = 0.05,
        resolution=(2, 10),
        **kwargs,
    ):
        self.from_atom = from_atom
        self.to_atom = to_atom
        self.thickness = thickness
        self.resolution = resolution
        super().__init__(*mobjects, **kwargs)
        if bond_type in [1]:
            self.bonds = self.add_single_bond()

        elif bond_type in [2, 5, 7]:
            self.bonds = self.add_double_bond()

        elif bond_type in [3]:
            self.bonds = self.add_triple_bond()

        else:
            raise Exception(
                f"Unknown or unsupported bond type {bond_type} at bond from atom {self.from_atom} to atom {self.to_atom}"
            )

        self.add(self.bonds)

    def half_bond(self, start, end, color, shift):
        return Line3D(
            np.array(start) + shift,
            np.array(end) + shift,
            thickness=self.thickness,
            color=color,
            resolution=self.resolution,
        )

    def add_lines(self, shifts):
        bond = VGroup()
        start = np.array(self.from_atom.coords, dtype=float)
        end = np.array(self.to_atom.coords, dtype=float)
        midpoint = (start + end) / 2
        for shift in shifts:
            bond.add(
                VGroup(
                    self.half_bond(start, midpoint, self.from_atom.element.color, shift),
                    self.half_bond(end, midpoint, self.to_atom.element.color, shift),
                )
            )
        return bond

    def add_single_bond(self):
        return self.add_lines([np.zeros(3)])

    def add_double_bond(self):
        perp_unit = self.get_perpendicular_unit_vector(
            self.from_atom.coords, self.to_atom.coords
        )
        return self.add_lines([0.12 * perp_unit, -0.12 * perp_unit])

    def add_triple_bond(self):
        perp_unit = self.get_perpendicular_unit_vector(
            self.from_atom.coords, self.to_atom.coords
        )
        return self.add_lines([np.zeros(3), -0.15 * perp_unit, 0.15 * perp_unit])

    def get_perpendicular_unit_vector(self, point_a, point_b):
        direction = np.array(point_b, dtype=float) - np.array(point_a, dtype=float)
        if direction[0] == 0 and direction[1] == 0:
            perp_vector = np.cross(direction, np.array([0, 1, 0]))

        else:
            perp_vector = np.cross(direction, np.array([0, 0, 1]))

        return perp_vector / np.linalg.norm(perp_vector)

import numpy as np

from manim import Sphere

from ..element import Element


class ThreeDAtom(Sphere):
    """
    Used to draw a sphere which represents an atom.
    Uses an Element to get data.

    Works with Manim's usual (Cairo) renderer: draw it in a ThreeDScene.
    """

    def __init__(
        self,
        element: Element,
        coords=np.array([0, 0, 0]),
        radius: float = 0.25,
        resolution=(16, 12),
        **kwargs,
    ):
        self.coords = np.array(coords, dtype=float)
        self.element = element
        kwargs.setdefault("fill_opacity", 1)
        kwargs.setdefault("stroke_width", 0)
        super().__init__(
            center=self.coords, radius=radius, resolution=resolution, **kwargs
        )
        self.set_color(element.color)

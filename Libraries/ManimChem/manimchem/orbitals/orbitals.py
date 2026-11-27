from math import factorial

import numpy as np

from manim import BLUE, ORIGIN, PI, RED, TAU, Surface, VGroup


def associated_legendre(l, m, x):
    """P_l^m(x) with the Condon-Shortley phase, for 0 <= m <= l (as scipy.special.lpmv)."""
    pmm = 1.0
    if m > 0:
        somx2 = np.sqrt(max(0.0, (1 - x) * (1 + x)))
        fact = 1.0
        for _ in range(m):
            pmm *= -fact * somx2
            fact += 2
    if l == m:
        return pmm
    pmmp1 = x * (2 * m + 1) * pmm
    if l == m + 1:
        return pmmp1
    pll = 0.0
    for ll in range(m + 2, l + 1):
        pll = (x * (2 * ll - 1) * pmmp1 - (ll + m - 1) * pmm) / (ll - m)
        pmm, pmmp1 = pmmp1, pll
    return pll


def spherical_harmonic_real_part(l, m, azimuth, polar):
    """The real part of Y_l^m(azimuth, polar), as `scipy.special.sph_harm(m, l, azimuth, polar).real`."""
    k = abs(m)
    if k > l:
        return 0.0
    norm = np.sqrt((2 * l + 1) / (4 * PI) * factorial(l - k) / factorial(l + k))
    value = norm * associated_legendre(l, k, np.cos(polar)) * np.cos(k * azimuth)
    return (-1) ** k * value if m < 0 else value


class OrbitalBase(Surface):
    """
    Base class for implementing atomic orbitals.
    Not meant to be used directly even when you can.

    Works with Manim's usual (Cairo) renderer: draw it in a ThreeDScene.
    """

    def __init__(
        self,
        center=ORIGIN,
        resolution=(32, 16),
        u_range=(0, PI),
        v_range=(0, TAU),
        n_value=1,
        l_value=0,
        m_value=0,
        size=1,
        **kwargs,
    ):
        self.n_value = n_value
        self.l_value = l_value
        self.m_value = m_value
        self.size = size
        kwargs.setdefault("fill_opacity", 0.85)
        kwargs.setdefault("stroke_width", 0.5)

        super().__init__(
            self.uv_func,
            resolution=resolution,
            u_range=u_range,
            v_range=v_range,
            **kwargs,
        )

        self.shift(center)

    def psi_ang(self, phi, theta, l=0, m=0):
        return spherical_harmonic_real_part(l, m, phi, theta)

    def calculate_coordinates(self, psi, u, v):
        x = np.sin(u) * np.cos(v) * abs(psi)
        y = np.sin(u) * np.sin(v) * abs(psi)
        z = np.cos(u) * abs(psi)

        return self.size * np.array([x, y, z])

    def uv_func(self, u, v):
        psi = self.psi_ang(v, u, l=self.l_value, m=self.m_value)

        return self.calculate_coordinates(psi, u, v)


class OrbitalPositive(OrbitalBase):
    """
    Calculates the positive values of the orbital.
    """

    def uv_func(self, u, v):
        psi = self.psi_ang(v, u, l=self.l_value, m=self.m_value)
        if psi < 0:
            psi = 0

        return self.calculate_coordinates(psi, u, v)


class OrbitalNegative(OrbitalBase):
    """
    Calculates the negative values of the orbital.
    """

    def uv_func(self, u, v):
        psi = self.psi_ang(v, u, l=self.l_value, m=self.m_value)
        if psi > 0:
            psi = 0

        return self.calculate_coordinates(psi, u, v)


class Orbital(VGroup):
    """
    An atomic orbital's angular shape: its positive lobes (red) and its negative lobes (blue).
    n value is still not implemented TODO

    Works with Manim's usual (Cairo) renderer: draw it in a ThreeDScene.

    Examples
    ---------
    .. code-block:: python

        from manimchem import *

        class POrbital(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=60 * DEGREES, theta=30 * DEGREES)
                self.add(Orbital(l=1, m=0))
    """

    def __init__(
        self,
        n=None,
        l=0,
        m=0,
        size=3,
        positive_color=RED,
        negative_color=BLUE,
        resolution=(32, 16),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.n = n or l + 1
        self.l = l
        self.m = m
        self.size = size
        self.positive = OrbitalPositive(
            n_value=self.n, l_value=l, m_value=m, size=size, resolution=resolution
        ).set_color(positive_color)
        self.negative = OrbitalNegative(
            n_value=self.n, l_value=l, m_value=m, size=size, resolution=resolution
        ).set_color(negative_color)
        self.add(self.positive, self.negative)

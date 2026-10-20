import math

from manim import *


def bent_angle(theta, v1, v2):
    """Snell's law, sin(theta2) / v2 = sin(theta1) / v1: the refracted ray's angle, or None when the ray can't
    get through (total internal reflection)."""
    s = math.sin(theta) * v2 / v1
    return math.asin(s) if abs(s) <= 1 else None


def reach(direction, ray_length, width, depth):
    """The point ray_length along a unit direction from the center, or where the direction leaves the media if that
    comes first: nothing pokes out, so the object's center stays where the ray hits the boundary."""
    limits = [ray_length] + [edge / abs(d) for d, edge in zip(direction, (width / 2, depth)) if abs(d) > 1e-9]
    return min(limits) * np.array([direction[0], direction[1], 0])


def clip01(x):
    return min(max(x, 0), 1)


class Refraction(VGroup):
    """A light ray hitting the boundary between two media at the center and bending by Snell's law. Its parts, in
    order: top medium, bottom medium, normal line, incoming ray, outgoing ray, the two angle arcs, the two labels.
    A part that is switched off is an empty group, so the order never changes. When the ray can't get through,
    the outgoing ray is reflected back up and the bottom arc and label are left out."""

    def __init__(self, theta=40 * DEGREES, v1=1.0, v2=0.6, width=14.25, depth=4.0, ray_length=10.0,
                 ray_color="#FFFF00", ray_width=4.0, bottom_color="#1B3540", top_color="#000000", top_opacity=0.0,
                 normal=True, normal_length=2.0, line_color="#BBBBBB", arcs=True, arc_radius=0.8, labels=True,
                 label1=r"\theta_1", label2=r"\theta_2", **kwargs):
        super().__init__(**kwargs)
        # what it was made with, so its animations can make it again with another angle
        self.settings = dict(theta=theta, v1=v1, v2=v2, width=width, depth=depth, ray_length=ray_length,
                             ray_color=ray_color, ray_width=ray_width, bottom_color=bottom_color,
                             top_color=top_color, top_opacity=top_opacity, normal=normal,
                             normal_length=normal_length, line_color=line_color, arcs=arcs, arc_radius=arc_radius,
                             labels=labels, label1=label1, label2=label2)
        limit = 89 * DEGREES
        theta1 = max(-limit, min(limit, theta))
        theta2 = bent_angle(theta1, max(0.01, v1), max(0.01, v2))
        self.reflected = theta2 is None
        self.top_medium = Rectangle(width=width, height=depth, stroke_width=0, fill_color=top_color,
                                    fill_opacity=top_opacity).move_to(UP * depth / 2)
        self.bottom_medium = Rectangle(width=width, height=depth, stroke_width=0, fill_color=bottom_color,
                                       fill_opacity=1).move_to(DOWN * depth / 2)
        n = min(normal_length, depth)
        self.normal_line = Line(UP * n, DOWN * n, stroke_color=line_color,
                                stroke_width=2) if normal else VGroup()
        start = reach((-math.sin(theta1), math.cos(theta1)), ray_length, width, depth)
        out = (math.sin(theta1), math.cos(theta1)) if self.reflected else (math.sin(theta2), -math.cos(theta2))
        end = reach(out, ray_length, width, depth)
        self.ray_in = Line(start, ORIGIN, stroke_color=ray_color, stroke_width=ray_width)
        self.ray_out = Line(ORIGIN, end, stroke_color=ray_color, stroke_width=ray_width)
        corners = [(PI / 2, theta1, label1)]  # (where the normal points, angle to the ray, label)
        if not self.reflected:
            corners.append((-PI / 2, theta2, label2))
        self.angle_arcs = [VGroup(), VGroup()]
        self.angle_labels = [VGroup(), VGroup()]
        for i, (side, angle, text) in enumerate(corners):
            if abs(angle) < 1e-3:
                continue
            if arcs:
                self.angle_arcs[i] = Arc(radius=arc_radius, start_angle=side, angle=angle,
                                         stroke_color=line_color, stroke_width=2)
            if labels and text.strip():
                middle = side + angle / 2
                self.angle_labels[i] = MathTex(text, font_size=40).move_to(
                    (arc_radius + 0.35) * np.array([math.cos(middle), math.sin(middle), 0]))
        self.add(self.top_medium, self.bottom_medium, self.normal_line, self.ray_in, self.ray_out, *self.angle_arcs,
                 *self.angle_labels)


# Shine: when each part comes in, as (from, to, drawn) over the animation (after its rate function): the media and
# the normal fade in, the ray draws in to the boundary and on, and each angle's arc and label fade in as its ray
# arrives. Drawn parts grow from their start; the others fade in.
SHINE = [(0, 0.3, False), (0, 0.3, False), (0.1, 0.35, False), (0.25, 0.6, True), (0.6, 0.95, True),
         (0.45, 0.65, False), (0.8, 1, False), (0.45, 0.65, False), (0.8, 1, False)]


class Shine(Animation):
    """Brings the refraction in, the light travelling through it."""

    def __init__(self, mobject, **kwargs):
        super().__init__(mobject, introducer=True, **kwargs)

    def interpolate_mobject(self, alpha):
        t = self.rate_func(alpha)
        parts, start = self.mobject.submobjects, self.starting_mobject.submobjects
        if len(parts) != len(SHINE) or len(start) != len(SHINE):  # not shaped like a Refraction
            self.mobject.become(self.starting_mobject).fade(1 - t)
            return
        for part, original, (a, b, drawn) in zip(parts, start, SHINE):
            s = clip01((t - a) / (b - a))
            if drawn:
                part.pointwise_become_partial(original, 0, s)
            else:
                part.become(original).fade(1 - s)


class SweepAngle(Animation):
    """The incoming ray turns to another angle, and the bent ray, the arcs and the labels follow it. It starts from
    the refraction's angle as it is and leaves it at `to`, wherever it was moved, turned or scaled to."""

    def __init__(self, mobject, to=70 * DEGREES, **kwargs):
        self.to = to
        self.settings = None
        super().__init__(mobject, **kwargs)

    def begin(self):
        self.settings = dict(getattr(self.mobject, "settings", None) or {}) or None
        if self.settings:
            # the media say where the boundary is now (its center), how big and which way up
            top, bottom = self.mobject.submobjects[:2]
            up = top.get_center() - bottom.get_center()
            self.hit = midpoint(top.get_center(), bottom.get_center())
            self.size = np.linalg.norm(up) / self.settings["depth"]
            self.turn = angle_of_vector(up) - PI / 2
            self.start_theta = self.settings["theta"]
        super().begin()

    def interpolate_mobject(self, alpha):
        if not self.settings:
            return
        theta = self.start_theta + (self.to - self.start_theta) * self.rate_func(alpha)
        fresh = Refraction(**{**self.settings, "theta": theta})
        fresh.scale(self.size, about_point=ORIGIN).rotate(self.turn, OUT, about_point=ORIGIN).shift(self.hit)
        self.mobject.become(fresh)

    def finish(self):
        super().finish()
        if self.settings:
            self.mobject.settings = {**self.settings, "theta": self.to}

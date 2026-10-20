// Refraction: the browser engine's version (Manimator draws and plays this one). kit.py is the same for Manim.
import {
  Animation, Arc, DEGREES, DOWN, Line, MathTex, ORIGIN, OUT, PI, Rectangle, UP, VGroup, angleOfVector, midpoint, mul,
  norm, sub,
} from "manimator";

/** Snell's law, sin(theta2) / v2 = sin(theta1) / v1: the refracted ray's angle, or null when the ray can't get
 * through (total internal reflection). */
function bentAngle(theta, v1, v2) {
  const s = Math.sin(theta) * v2 / v1;
  return Math.abs(s) <= 1 ? Math.asin(s) : null;
}

/** The point ray_length along a unit direction from the center, or where the direction leaves the media if that
 * comes first: nothing pokes out, so the object's center stays where the ray hits the boundary. */
function reach([dx, dy], rayLength, width, depth) {
  const limits = [rayLength];
  [[dx, width / 2], [dy, depth]].forEach(([d, edge]) => { if (Math.abs(d) > 1e-9) limits.push(edge / Math.abs(d)); });
  return mul([dx, dy, 0], Math.min(...limits));
}

const clip01 = (x) => Math.min(Math.max(x, 0), 1);

export class Refraction extends VGroup {
  static SIG = ["theta"]; // Refraction(30 * DEGREES) means theta=30 * DEGREES, as in Python

  __init__({ theta = 40 * DEGREES, v1 = 1.0, v2 = 0.6, width = 14.25, depth = 4.0, ray_length = 10.0,
    ray_color = "#FFFF00", ray_width = 4.0, bottom_color = "#1B3540", top_color = "#000000", top_opacity = 0.0,
    normal = true, normal_length = 2.0, line_color = "#BBBBBB", arcs = true, arc_radius = 0.8, labels = true,
    label1 = "\\theta_1", label2 = "\\theta_2", ...kw } = {}) {
    super.__init__(kw);
    // what it was made with, so its animations can make it again with another angle
    this.settings = { theta, v1, v2, width, depth, ray_length, ray_color, ray_width, bottom_color, top_color,
      top_opacity, normal, normal_length, line_color, arcs, arc_radius, labels, label1, label2 };
    const limit = 89 * DEGREES;
    const theta1 = Math.max(-limit, Math.min(limit, theta));
    const theta2 = bentAngle(theta1, Math.max(0.01, v1), Math.max(0.01, v2));
    this.reflected = theta2 === null;
    this.top_medium = Rectangle.make({ width, height: depth, stroke_width: 0, fill_color: top_color,
      fill_opacity: top_opacity }).move_to(mul(UP, depth / 2));
    this.bottom_medium = Rectangle.make({ width, height: depth, stroke_width: 0, fill_color: bottom_color,
      fill_opacity: 1 }).move_to(mul(DOWN, depth / 2));
    const n = Math.min(normal_length, depth);
    this.normal_line = normal ? Line.make({ start: mul(UP, n), end: mul(DOWN, n),
      stroke_color: line_color, stroke_width: 2 }) : VGroup.make();
    const start = reach([-Math.sin(theta1), Math.cos(theta1)], ray_length, width, depth);
    const end = reach(this.reflected ? [Math.sin(theta1), Math.cos(theta1)] : [Math.sin(theta2), -Math.cos(theta2)],
      ray_length, width, depth);
    this.ray_in = Line.make({ start, end: ORIGIN, stroke_color: ray_color, stroke_width: ray_width });
    this.ray_out = Line.make({ start: ORIGIN, end, stroke_color: ray_color, stroke_width: ray_width });
    const corners = [[PI / 2, theta1, label1]]; // [where the normal points, angle to the ray, label]
    if (!this.reflected) corners.push([-PI / 2, theta2, label2]);
    this.angle_arcs = [VGroup.make(), VGroup.make()];
    this.angle_labels = [VGroup.make(), VGroup.make()];
    corners.forEach(([side, angle, text], i) => {
      if (Math.abs(angle) < 1e-3) return;
      if (arcs) {
        this.angle_arcs[i] = Arc.make({ radius: arc_radius, start_angle: side, angle, stroke_color: line_color,
          stroke_width: 2 });
      }
      if (labels && String(text).trim()) {
        const middle = side + angle / 2;
        this.angle_labels[i] = MathTex.make({ tex_strings: [String(text)], font_size: 40 }).move_to(
          mul([Math.cos(middle), Math.sin(middle), 0], arc_radius + 0.35));
      }
    });
    this.add(this.top_medium, this.bottom_medium, this.normal_line, this.ray_in, this.ray_out, ...this.angle_arcs,
      ...this.angle_labels);
    return this;
  }
}

// Shine: when each part comes in, as [from, to, drawn] over the animation (after its rate function): the media and
// the normal fade in, the ray draws in to the boundary and on, and each angle's arc and label fade in as its ray
// arrives. Drawn parts grow from their start; the others fade in.
const SHINE = [[0, 0.3, false], [0, 0.3, false], [0.1, 0.35, false], [0.25, 0.6, true], [0.6, 0.95, true],
  [0.45, 0.65, false], [0.8, 1, false], [0.45, 0.65, false], [0.8, 1, false]];

/** Shine: brings the refraction in, the light travelling through it. */
export class Shine extends Animation {
  __init__({ mobject = null, ...kw } = {}) {
    return super.__init__({ ...kw, mobject, introducer: true });
  }

  interpolate_mobject(alpha) {
    const t = this.rate_func(alpha);
    const parts = this.mobject.submobjects;
    const start = this.starting_mobject.submobjects;
    if (parts.length !== SHINE.length || start.length !== SHINE.length) { // not shaped like a Refraction
      this.mobject.become(this.starting_mobject).fade(1 - t);
      return;
    }
    SHINE.forEach(([from, to, drawn], i) => {
      const s = clip01((t - from) / (to - from));
      if (drawn) parts[i].pointwise_become_partial(start[i], 0, s);
      else parts[i].become(start[i]).fade(1 - s);
    });
  }
}

/** Sweep angle: the incoming ray turns to another angle, and the bent ray, the arcs and the labels follow it. It
 *  starts from the refraction's angle as it is and leaves it at `to`, wherever it was moved, turned or scaled to. */
export class SweepAngle extends Animation {
  __init__({ mobject = null, to = 70 * DEGREES, ...kw } = {}) {
    this.to = to;
    this.settings = null;
    return super.__init__({ ...kw, mobject });
  }

  begin() {
    this.settings = this.mobject.settings ? { ...this.mobject.settings } : null;
    if (this.settings) {
      // the media say where the boundary is now (its center), how big and which way up
      const [top, bottom] = this.mobject.submobjects;
      const up = sub(top.get_center(), bottom.get_center());
      this.hit = midpoint(top.get_center(), bottom.get_center());
      this.size = norm(up) / this.settings.depth;
      this.turn = angleOfVector(up) - PI / 2;
      this.start_theta = this.settings.theta;
    }
    super.begin();
  }

  interpolate_mobject(alpha) {
    if (!this.settings) return;
    const theta = this.start_theta + (this.to - this.start_theta) * this.rate_func(alpha);
    const fresh = Refraction.make({ ...this.settings, theta });
    fresh.scale(this.size, { about_point: ORIGIN }).rotate(this.turn, OUT, { about_point: ORIGIN }).shift(this.hit);
    this.mobject.become(fresh);
  }

  finish() {
    super.finish();
    if (this.settings) this.mobject.settings = { ...this.settings, theta: this.to };
  }
}

# AGENTS.md

This repo is for writing Manimator customizations. Each customization is one object written in code, plus up to
10 animations made for it. You write each one twice, as JavaScript (`kit.js`, which Manimator runs in the
browser) and as Python (`kit.py`, which Manim runs when a project is downloaded as Python), and both must draw
the same thing.

## Layout

```
Kits/<Name>/manifest.json   names, class names, settings shown in the editor
Kits/<Name>/kit.js          the classes in JavaScript (Manimator draws this)
Kits/<Name>/kit.py          the same classes in Python (Manim renders this)
Kits/<Name>/README.md       optional, shown to users
Build.py                    checks a kit and zips it into Builds/<Name>.manimkit
```

Name folders in PascalCase, matching the object's class (`Kits/Pendulum` for `Pendulum`).

## Workflow

1. Start a new kit by copying the closest example: `Battery` (smallest), `Refraction` (angles, LaTeX, an
   animation that rebuilds its object), or `NeuralNetwork` (many parts, an animation across them).
2. Write `kit.py` first if you know Manim, then port it line by line to `kit.js`.
3. Run `python Build.py Kits/<Name>`. Fix every error it prints. Exit code 0 means it passed.
4. The user uploads `Builds/<Name>.manimkit` on Manimator's Customizations page. Only Manimator can show how
   it looks; `Build.py` checks structure only, not drawing.

`Build.py` runs Manimator's upload checks except one: Manimator also rejects class names that Manim or Manimator
already use (`Circle`, `FadeIn`, `Arrow`...). Pick distinctive names.

## manifest.json

```json
{
  "manimkit": 2,
  "name": "Battery",
  "version": "1.1",
  "description": "A battery whose fill shows its charge",
  "license": "MIT",
  "object": {
    "class": "Battery",
    "style": "none",
    "params": [
      {"name": "charge", "kind": "float", "default": 0.7, "min": 0, "max": 1, "step": 0.05,
       "slider": true, "label": "Charge", "tooltip": "0 is empty, 1 is full"}
    ]
  },
  "animations": [
    {"class": "PopIn", "name": "Pop in", "description": "Grow in and settle",
     "introducer": true, "run_time": 0.8,
     "params": [{"name": "bounce", "kind": "float", "default": 1.7, "min": 0, "max": 5, "label": "Bounce"}]}
  ]
}
```

- `manimkit` is always `2`. `name` is required (up to 40 chars), `description` up to 200.
- `object.class` and each `animations[].class`: PascalCase, unique, and defined in both `kit.py` and `kit.js`.
- `object.style` controls which color controls the editor shows: `"none"` (the object keeps its own colors),
  `"shape"` (stroke and fill), `"line"` or `"text"`.
- Each animation can have `"introducer": true` (it brings the object on screen, like FadeIn) or
  `"remover": true` (it takes the object away, like FadeOut), but not both. Your class must pass the same
  flag (`introducer=True` in Python). `run_time` is between 0.05 and 60 seconds (default 1).
- `params`: up to 20 per object and per animation. Each one is passed to your class as a keyword argument with
  the same name, so the class must accept it. Names are lowercase Python names, and can't be one of `mobject`,
  `run_time`, `rate_func`, `lag_ratio`, `name`, `target`, `dim`, `z_index`, `introducer` or `remover`.
- Param kinds: `float` and `int` (with `min`, `max`, `step`, `decimals`, `slider`), `bool`, `color`
  (`"#RRGGBB"`), `str` (one line), `text` (multi-line), `font`, `angle`, `point` and `vector` (`[x, y]`),
  `direction` (`"UP"`, `"DL"`, ...; optional `choices`), and `enum` (`choices`: text, or `[value, label]`).
  Every param can have `default`, `label` (up to 40 chars) and `tooltip` (up to 160).
- **Angles are degrees in the manifest and the editor, but radians in your code.** A default of `40` arrives
  as `40 * DEGREES`.
- A new version of an uploaded kit must keep `object.class`; everything else may change.

## kit.js

```js
import { Animation, GREEN, LEFT, RIGHT, Rectangle, RoundedRectangle, VGroup, WHITE, mul } from "manimator";

export class Battery extends VGroup {
  static SIG = ["charge"]; // positional arguments, as in Python: Battery(0.5) means charge=0.5

  __init__({ charge = 0.7, ...kw } = {}) {
    super.__init__(kw);
    const body = RoundedRectangle.make({ width: 2, height: 1, corner_radius: 0.12, color: WHITE });
    const fill = Rectangle.make({ width: 1.8 * charge, height: 0.8, stroke_width: 0, fill_color: GREEN,
      fill_opacity: 1 });
    fill.align_to(body, LEFT).shift(mul(RIGHT, 0.1));
    this.add(body, fill);
    return this;
  }
}

export class PopIn extends Animation {
  __init__({ mobject = null, bounce = 1.7, ...kw } = {}) {
    this.bounce = bounce;
    return super.__init__({ ...kw, mobject, introducer: true });
  }

  interpolate_mobject(alpha) {
    const t = this.rate_func(alpha) - 1;
    this.mobject.become(this.starting_mobject);
    this.mobject.scale(Math.max(1 + (this.bounce + 1) * t ** 3 + this.bounce * t ** 2, 0.001));
  }
}
```

- Import only from `"manimator"`. No other imports and no `import()`. The code runs in a sandbox with no
  network, DOM or account access; it can only draw.
- `"manimator"` exports Manim's object and animation classes, the constants (`UP`, `RIGHT`, `ORIGIN`, `PI`,
  `DEGREES`...), named colors as hex strings (`GREEN`, `BLUE_C`...), the rate functions, and vector helpers.
- Export every class by its name (`export class Battery`). Don't use `export default`.
- Make objects with `Cls.make({...})`, which is Python's `Cls(...)` with keyword arguments.
- Put setup in `__init__({ ...named args, ...kw } = {})`. Call `super.__init__(kw)` and end with `return this`.
- Methods take the same arguments in the same order as in Python: `a.next_to(b, RIGHT, 0.5)`.
- JavaScript has no operators on vectors, so use the helpers: `mul(RIGHT, 2)` for `RIGHT * 2`, `add(a, b)` for
  `a + b`, `sub(a, b)` for `a - b`, plus `norm`, `midpoint` and `angleOfVector`.
- An animation extends `Animation`, takes `mobject` and changes `this.mobject` in
  `interpolate_mobject(alpha)`. Apply `this.rate_func(alpha)` yourself.
- `this.mobject` is always an instance of your own object class. An animation can therefore use the parts or
  settings the object kept (for example `this.settings`), or rebuild it with other settings. Refraction's
  `SweepAngle` does this.

## kit.py

```python
from manim import *


class Battery(VGroup):
    def __init__(self, charge=0.7, **kwargs):
        super().__init__(**kwargs)
        ...


class PopIn(Animation):
    def __init__(self, mobject, bounce=1.7, **kwargs):
        self.bounce = bounce
        super().__init__(mobject, introducer=True, **kwargs)

    def interpolate_mobject(self, alpha):
        ...
```

- Plain Manim Community. Define every class from the manifest at the top level of the file.
- Manimator only parses this file and never runs it. It goes into the `customizations` folder of a project's
  Python download, and that project's `scene.py` imports it. Test it yourself in Manim if you can:
  `manim -pql` with a small scene that adds the object and plays each animation.

## Rules that matter

- **Keep the two files matched.** Same classes, same parameters with the same defaults, same parts added in the
  same order, same geometry and colors. What users see in Manimator is the JS; what Manim renders is the Python.
  When you change one, change the other in the same edit.
- Clamp settings to safe ranges in code (as Battery clamps `charge`), because users can type any value.
- When an optional part is turned off, add an empty `VGroup` in its place so the order of parts never changes
  (Refraction does this). Animations rely on that order.
- Limits: `kit.js` and `kit.py` up to 256 KB each, `manifest.json` and `README.md` up to 64 KB each, and the
  whole `.manimkit` file up to 1 MB.
- `Builds/` is generated output. Don't edit it or commit it.

## Reference

- Full guide: <https://manimator.app/docs/customizations>
- The three folders in `Kits/` are working, uploaded examples. When unsure how to do something, copy what they do.

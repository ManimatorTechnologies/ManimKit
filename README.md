# ManimKit

Write your own **customizations** for [Manimator](https://manimator.app): a new object, written in code, with
the animations made for it. When you upload one, its object shows up in the editor next to Manim's own objects,
and its animations play on it.

This repo has three working examples to start from, plus a script that checks your customization and packs it
into a `.manimkit` file ready to upload.

## Quick start

1. Fork or copy this repo.
2. Copy an example folder in `Kits/` and rename it, for example `Kits/Pendulum`.
3. Edit its four files (see below).
4. Run `python Build.py Kits/Pendulum` (Python 3.9+, nothing to install). It checks the files and writes
   `Builds/Pendulum.manimkit`.
5. In Manimator, open **Customizations**, upload the file, and try it in a project.

Running `python Build.py` on its own builds every folder in `Kits/`.

## What's in a customization

| File | What it is |
|---|---|
| `manifest.json` | The name, the object's and animations' class names, and the settings the editor shows |
| `kit.js` | The classes in JavaScript. Manimator runs this to draw and play your object in the browser |
| `kit.py` | The same classes in Python, for Manim. Used when someone downloads their project as Python |
| `README.md` | Optional: how to use it, shown on the customization's page |

You write the object twice, once in JavaScript and once in Python, and both versions must draw the same thing.
Both are written the way Manim's own classes are written.

## The examples

| Kit | Shows how to |
|---|---|
| [Battery](Kits/Battery) | The smallest one: an object with one setting, and a "Pop in" animation |
| [Refraction](Kits/Refraction) | Angle settings, LaTeX labels, and an animation that rebuilds the object with new settings |
| [NeuralNetwork](Kits/NeuralNetwork) | A 3Blue1Brown-style network, with an animation that plays across its parts |

## Learn more

- [AGENTS.md](AGENTS.md) has the full rules. It's written for AI coding agents, but people can read it too.
- The Customizations guide in Manimator's docs: <https://manimator.app/docs/customizations>

## License

MIT. See [LICENSE](LICENSE). Your own customizations can use any license; set it in `manifest.json`.

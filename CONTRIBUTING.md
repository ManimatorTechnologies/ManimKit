# Sharing a customization in the gallery

Manimator's gallery is this repository: each folder in `Kits/` is one customization, and anyone signed in to
[Manimator](https://manimator.app) can add it to their projects. To share yours, add its folder with a pull request.
Once the pull request is merged, it joins the gallery within minutes, credited to your GitHub name.

## Adding one

1. Fork this repository.
2. Make your customization in `Kits/<Name>`, named after its object's class (`Kits/Pendulum` for `Pendulum`).
   [AGENTS.md](AGENTS.md) has the format and the rules for `kit.js` and `kit.py`; the examples in `Kits/` show them.
3. In `manifest.json`, set `"author"` to your GitHub user name and `"license"` to `"MIT"`.
4. Run `python Build.py Kits/<Name>`. It checks the files and writes `Builds/<Name>.manimkit`.
5. Upload that file to your own Customizations in Manimator and try it in a project. Only Manimator shows how it
   really draws and plays.
6. Open a pull request with just that folder.

A check runs on every pull request. Then a maintainer reads the code and tries it, and merges it or asks for changes.
Code in the gallery runs in everyone's browser, so every pull request is read by a person before it is merged.

## Changing one

Change the files in its folder and give it a new `"version"` in `manifest.json`. Once merged, it becomes the
customization's next version: projects keep the version they were made with until their owner updates them, so a
version never changes after it is merged. Keep the object's class; a new class is a new customization in a new folder.

Only a customization's author, or a maintainer, can change or remove it. To suggest a change to someone else's, open
an issue.

## What gets merged

- One customization per pull request, with only its own files: `manifest.json`, `kit.js`, `kit.py`, `README.md`.
- Your own work. Code copied from elsewhere must have a license that allows MIT (Manim's own code does;
  3Blue1Brown's videos repository doesn't, as it is CC BY-NC-SA).
- `kit.js` and `kit.py` that draw the same thing.
- Class names no other customization here uses.
- Nothing that tracks people, reaches the network or does anything but draw. The sandbox it runs in blocks most of
  that; review catches the rest.

## License

Everything here, your customization too, is under the [MIT license](LICENSE). By opening a pull request you agree
that what you add is shared under it.

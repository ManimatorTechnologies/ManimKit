# Adding a library

Each folder in `Libraries/` is one library, a Python package written in Manim, and every library here is in everyone's
[Manimator](https://manimator.app): its objects and animations are in the editor for anyone, guest or not. To add
yours, add its folder with a pull request. Once the pull request is merged, it is in Manimator within minutes,
credited to your GitHub name.

## Adding one

1. Fork this repository.
2. Make your library in `Libraries/<Name>`, named after its package (`Libraries/Pendulums` for `pendulums`).
   [AGENTS.md](AGENTS.md) has the format and the rules; `Libraries/ManimChem` shows them.
3. In `manifest.json`, set `"author"` to your GitHub user name, `"license"` to `"MIT"`, and `"category"` to the
   name of its group in the palette (such as `"Chemistry"`).
4. Run `python Build.py Libraries/<Name>`. It checks the files.
5. Try it in Manimator (below): only Manimator shows how its objects really draw and play.
6. Open a pull request with just that folder.

A check runs on every pull request. Then a maintainer reads the code and tries it, and merges it or asks for changes.
A library runs in everyone's browser, so every pull request is read by a person before it is merged.

## Trying it in Manimator

Manimator is open source, so run it on your own computer and point it at your fork's branch. In a copy of
[Manimator](https://github.com/ManimatorTechnologies/Manimator), set these before starting it (`Manimator.bat` or
`python run.py`):

    MANIMATOR_KITS_REPO=<your GitHub name>/ManimKit
    MANIMATOR_KITS_BRANCH=<your branch>

Push to the branch and restart Manimator (it also looks again every 15 minutes): your library's objects are in the
editor's palette.

## Changing one

Change the files in its folder and give it a new `"version"` in `manifest.json`. Once merged, it becomes the
library's next version: projects keep the version they were made with until their owner updates them, so a version
never changes after it is merged. Keep the package name; a new package is a new library in a new folder.

Only a library's author, or a maintainer, can change or remove it. To suggest a change to someone else's, open an
issue.

## What gets merged

- One library per pull request, with only its own files: `manifest.json`, `README.md`, its license and its package
  folder.
- Your own work, or code under a license that allows MIT (Manim's own code does; 3Blue1Brown's videos repository
  doesn't, as it is CC BY-NC-SA). Keep the original copyright notice of code you fork.
- At least one object or animation in `manifest.json`: people use a library through the editor.
- Classes and a package name no other library here uses.
- Nothing that tracks people, reaches the network or does anything but draw. The sandbox it runs in blocks most of
  that (PubChem's data is the one thing it may read); review catches the rest.

## License

Everything here, your library too, is under the [MIT license](LICENSE). By opening a pull request you agree that what
you add is shared under it.

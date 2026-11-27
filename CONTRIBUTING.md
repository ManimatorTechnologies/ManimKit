# Sharing a customization in the gallery

Manimator's gallery is this repository: each folder in `Libraries/` is one customization, a Python library, and
anyone signed in to [Manimator](https://manimator.app) can add it and use it in the editor and the Code view. To share
yours, add its folder with a pull request. Once the pull request is merged, it joins the gallery within minutes,
credited to your GitHub name.

## Adding one

1. Fork this repository.
2. Make your customization in `Libraries/<Name>`, named after its package (`Libraries/Pendulums` for `pendulums`).
   [AGENTS.md](AGENTS.md) has the format and the rules; `Libraries/ManimChem` shows them.
3. In `manifest.json`, set `"author"` to your GitHub user name and `"license"` to `"MIT"`.
4. Run `python Build.py Libraries/<Name>`. It checks the files and writes `Builds/<Name>.manimkit`.
5. Upload that file to your own Customizations in Manimator and try it in the editor and the Code view. Only
   Manimator shows how it really draws and plays.
6. Open a pull request with just that folder.

A check runs on every pull request. Then a maintainer reads the code and tries it, and merges it or asks for changes.
Code in the gallery runs in everyone's browser, so every pull request is read by a person before it is merged.

## Changing one

Change the files in its folder and give it a new `"version"` in `manifest.json`. Once merged, it becomes the
customization's next version: projects keep the version they were made with until their owner updates them, so a
version never changes after it is merged. Keep the package name; a new package is a new customization in a new
folder.

Only a customization's author, or a maintainer, can change or remove it. To suggest a change to someone else's, open
an issue.

## What gets merged

- One customization per pull request, with only its own files: `manifest.json`, `README.md`, its license and its
  package folder.
- Your own work, or code under a license that allows MIT (Manim's own code does; 3Blue1Brown's videos repository
  doesn't, as it is CC BY-NC-SA). Keep the original copyright notice of code you fork.
- Classes and a package name no other customization here uses.
- Nothing that tracks people, reaches the network or does anything but draw. The sandbox it runs in blocks most of
  that (PubChem's data is the one thing it may read); review catches the rest.

## License

Everything here, your customization too, is under the [MIT license](LICENSE). By opening a pull request you agree
that what you add is shared under it.

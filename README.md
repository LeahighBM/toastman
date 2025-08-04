# toastman
A terminal-based UI (TUI) for making REST Requests. Like Postman, but with a "T"... and an "A"

## Getting started 
This project uses `uv` for managing packages and dependencies. To install and use `uv` you can follow [Astral's documentation](https://docs.astral.sh/uv/getting-started/installation/). 

To sync dependencies from the lockfile use `uv sync`.

To update all packages, use either `uv sync --upgrade` or `uv lock --upgrade`.

This project uses the Textual library for Terminal UI building. You can check out their documentation [here](https://textual.textualize.io/widgets/button/)

## Running 
To run: `python main.py`. The terminal should look similar to the screenshot below, although some default terminal emulators make a mess of things. Ones that look as expected are the VSCode integrated terminal (below) and [ghostty](https://ghostty.org/).

![](misc/Toastman.png?)
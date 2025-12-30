# md2electraone

This is a Python program that attempts to generate presets for the [Electra One](https://electra.one/) MIDI controller from
markdown documents that describe the MIDI implementation of instruments.

See example source documents in the /specs folder.

## Setting up Python

If you are not tech savvy, this may help:

- install Python if you don't have it (see https://python.org)
- download and install this repo (use git clone if you know how to, else download from https://github.com/gramster/md2electraone/archive/refs/heads/main.zip and unzip in a folder).
- open a terminal or shell and change to this folder
- you now want to create a "virtual environment" so you don't mess up your system Python. Run these commands:
    - `python3 -m venv .venv`
    - `. .venv/bin/activate` (on Mac/Linux) or `.venv\\bin\\activate.bat` on Windows (I think)
    - `python3 -m ensurepip`
    - `python3 -m pip install -e .`
    After this the commands below should work.

## Using the App

Generate JSON only:

    python3 -m md2electraone "specs/ndlr2.md" -o NDLR_ElectraOne_Preset.json --debug

Replace specs/ndlr2.md here with your markdown file. You can then import the output JSON file on the Electra website to your presets.

Generate JSON + cleaned markdown:

    python3 md2electraone "specs/ndlr2.md" -o NDLR_ElectraOne_Preset.json --clean-md "NDLR MIDI.cleaned.md" --debug

Contributions of new Markdown specs welcomed!

## Markdown Requirements

You should have section headers followed by Markdown tables, with these columns:

- "CC (Hex)" - the CC number in hexadecimal. You can also do "CC" and use decimal.
- "Target" - the label to put on the control
- "Range" - the numeric range of the argument; e.g. 1-127
- "Choices" - for lists and buttons, comma-separated list of labels. If the number of labels is not the same as the range, then these should specify the appropriate numeric value in parenthese after the label.
- "Color" - RGB color code in hex. Carries through following rows until a new one is encountered

You can use blank rows in the table to create blank control spaces in the layout.

See specs/ for examples of input.

## Current Limitations

- only supports sending 7-bit CCs, no NRPN or SysEx
- output only; does not read from instruments
- only supports lists, faders and buttons


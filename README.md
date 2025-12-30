# md2electraone

This is a Python program that attempts to generate presets for the [Electra One](https://electra.one/) MIDI controller from
markdown documents that describe the MIDI implementation of instruments.

See example source documents in the /specs folder.

Generate JSON only:

    python3 md2electraone.py "specs/NDLR MIDI.md" -o NDLR_ElectraOne_Preset.json --debug

Generate JSON + cleaned markdown:

    python3 md2electraone.py "specs/NDLR MIDI.md" -o NDLR_ElectraOne_Preset.json --clean-md "NDLR MIDI.cleaned.md" --debug


## Notes

- The layout parameters are controllable via frontmatter under electra. In particular, if your MK2 is still “eating” the last column, the most useful knobs are:
    - electra.screen_width_controls (defaults to 800)
    - electra.right_padding
    - electra.cell_width (force a fixed width)
- Lists only render when Choices/Options exists (or the description matches an exact enumeration). Since you updated the markdown to put options only where needed, this script honors that.
- It tries hard to deal with imperfect tables, but if you have tables without divider rows (|---|---|), they won’t be recognized as tables.


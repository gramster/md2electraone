# md2electraone

**md2electraone** is a Python tool that converts between **Markdown documents** and **Electra One preset JSON** files.

Instead of hand-building Electra presets, you write (or reuse) a clean, readable Markdown spec of CC mappings — and this tool turns it into an importable Electra One preset JSON. You can also convert existing Electra One presets back to Markdown for documentation or editing.

Example input specs live in the `specs/` folder.

---

## What this does (and why)

- ✔ Convert Markdown tables → Electra One preset JSON
- ✔ Convert Electra One preset JSON → Markdown (reverse conversion)
- ✔ Enforce consistent layout and labeling
- ✔ Make MIDI implementations readable *and* executable
- ✔ Enable rapid iteration and sharing of controller mappings

I prefer this approach to designing a preset in a GUI editor, as it is easier to audit, make
quick bulk rearrangements, and potentially use the markdown doc elsewhere.

---

## Quick Start

If you already use Python:

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -e .
```

Then:

```bash
python3 -m md2electraone specs/ndlr2.md \
  -o NDLR_ElectraOne_Preset.json \
  --debug
```

Upload the generated JSON to the Electra One web editor and sync it to your device.

---

## Setting up Python (beginner-friendly)

If you’re not especially tech-savvy, follow this step by step:

1. **Install Python**  
   Download from https://python.org (Python 3.12+ required).

2. **Download this repository**
   - If you know Git:  
     ```bash
     git clone https://github.com/gramster/md2electraone.git
     ```
   - Otherwise:  
     Download and unzip  
     https://github.com/gramster/md2electraone/archive/refs/heads/main.zip

3. **Open a terminal / shell**
   - macOS: Terminal
   - Windows: PowerShell
   - Linux: your terminal of choice

4. **Change into the project folder**
   ```bash
   cd md2electraone
   ```

5. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   ```

   Activate it:
   - macOS / Linux:
     ```bash
     source .venv/bin/activate
     ```
   - Windows:
     ```bat
     .venv\Scripts\activate
     ```

7. **Install the tool**
   ```bash
   python3 -m ensurepip
   python3 -m pip install -e .
   ```

After this, the commands below should work as long as you run that within that folder.
If you need to use the tool again later, change to the folder and run the activate line only
first. If you want to get the latest update first:

6. **Update the tool**
   ```bash
   git pull
   python3 -m pip install -e .
   ```

If this seems like a big hassle to you, go vote on https://github.com/gramster/md2electraone/issues/1

---

## Usage

### Markdown → JSON (Generate preset)

Generate preset JSON only:

```bash
python3 -m md2electraone specs/ndlr2.md \
  -o NDLR_ElectraOne_Preset.json \
  --debug
```

Generate preset JSON **and** cleaned Markdown:

```bash
python3 -m md2electraone specs/ndlr2.md \
  -o NDLR_ElectraOne_Preset.json \
  --clean-md NDLR_MIDI.cleaned.md \
  --debug
```

The cleaned Markdown is useful if your source spec is messy or inconsistent.

### JSON → Markdown (Reverse conversion)

Convert an Electra One preset JSON back to Markdown:

```bash
python3 -m md2electraone NDLR_ElectraOne_Preset.json \
  --to-markdown \
  -o NDLR_spec.md \
  --debug
```

This is useful for:
- Documenting existing presets
- Extracting MIDI implementation from presets
- Editing presets in Markdown format
- Sharing preset specifications in a readable format

**Note:** The reverse conversion supports the subset of Electra One features that md2electraone can generate (7-bit CC messages, faders, lists, and pads). Any unsupported features will trigger warnings on stderr and will be dropped from the output.

### JSON output formatting

By default, the generated JSON is **minified** (compact, no whitespace) for optimal file size. For debugging or readability, use the `--pretty` flag to format the JSON with indentation:

```bash
python3 -m md2electraone specs/ndlr2.md \
  -o NDLR_ElectraOne_Preset.json \
  --pretty
```

**Note:** The Electra One accepts both minified and pretty-printed JSON, so use whichever format suits your workflow.

---

## Markdown Format

Each Markdown file should consist of:

- Optional **YAML frontmatter** (for metadata)
- Section headers (`## Pad`, `## Drone`, etc.)
- Followed by **Markdown tables**

### Optional frontmatter

You can include YAML frontmatter at the start of your Markdown file to specify device metadata:

```yaml
---
name: Moog Subsequent 37        # Device name (used in preset and devices array)
version: 2                       # Preset version (default: 2)
port: 1                          # MIDI port (default: 1)
channel: 5                       # MIDI channel (default: 1)
manufacturer: Moog Music         # Manufacturer (informational)
---
```

All fields are optional. If not specified, defaults will be used.

### Required table columns

| Column        | Description |
|---------------|-------------|
| **CC (Hex)**  | MIDI CC number in hexadecimal (`0x10`). You may also use `CC` with decimal values. For envelope controls, use comma-separated CC numbers (e.g. `1,2,3,4` for ADSR). |
| **Target**    | Label shown on the Electra One control |
| **Range**     | Numeric range (e.g. `0–127`) |
| **Choices**   | For lists/buttons: comma-separated labels. If needed, specify values in parentheses (`Minor(2)`). For envelope controls: `ADSR` or `ADR`. |
| **Color**     | RGB hex color (e.g. `#FF8800`). Persists until changed |

### Layout notes

- Blank rows in tables create **blank spaces** in the Electra layout
- Color values persist until overridden
- Section boundaries define logical control groupings

See the `specs/` directory for complete, working examples.

---

## Supported Control Types

md2electraone supports the following Electra One control types:

- **Faders** - Continuous value controls (default for controls without choices)
- **Lists** - Multi-valued selection controls (when choices are specified)
- **Pads** - Toggle buttons for on/off controls (when exactly 2 choices with on/off semantics)
- **ADSR Envelopes** - Attack, Decay, Sustain, Release envelope controls (specify `ADSR` in Choices column with 4 comma-separated CCs)
- **ADR Envelopes** - Attack, Decay, Release envelope controls (specify `ADR` in Choices column with 3 comma-separated CCs)

### Envelope Control Example

```markdown
| CC (Dec) | Label | Range | Choices |
|----------|-------|-------|---------|
| 1,2,3,4  | Filter ADSR | 0-127 | ADSR |
| 5,6,7    | Amp ADR     | 0-127 | ADR  |
```

Envelope controls automatically span 2 grid positions and create the appropriate multi-value structure with inputs mapped to the envelope components.

---

## Current Limitations

### Markdown → JSON conversion:
- Only **7-bit CC** messages supported
  (no NRPN or SysEx yet)
- **One-way output only**
  (does not read or sync from instruments)

### JSON → Markdown conversion:
- Only supports the subset of Electra One features that md2electraone can generate
- Unsupported features (groups, NRPN, SysEx, etc.) will be dropped with warnings
- Control positioning information is lost (regenerated based on page order)
- Multiple devices are not fully supported (only first device metadata is preserved)

---

## Contributing

Contributions are welcome!

- New Markdown specs
- Bug reports
- Improvements to layout rules or parsing

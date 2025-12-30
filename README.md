# md2electraone

**md2electraone** is a Python tool that generates presets for the  
**Electra One** MIDI controller from **Markdown documents** describing an instrument’s MIDI implementation.

Instead of hand-building Electra presets, you write (or reuse) a clean, readable Markdown spec of CC mappings — and this tool turns it into an importable Electra One preset JSON.

Example input specs live in the `specs/` folder.

---

## What this does (and why)

- ✔ Convert Markdown tables → Electra One preset JSON
- ✔ Enforce consistent layout and labeling
- ✔ Make MIDI implementations readable *and* executable
- ✔ Enable rapid iteration and sharing of controller mappings

Think of the Markdown file as the **single source of truth** for your controller.

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
   Download from https://python.org (Python 3.9+ recommended).

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

6. **Install the tool**
   ```bash
   python3 -m ensurepip
   python3 -m pip install -e .
   ```

After this, the commands below should work.

---

## Usage

### Generate preset JSON only

```bash
python3 -m md2electraone specs/ndlr2.md \
  -o NDLR_ElectraOne_Preset.json \
  --debug
```

### Generate preset JSON **and** cleaned Markdown

```bash
python3 -m md2electraone specs/ndlr2.md \
  -o NDLR_ElectraOne_Preset.json \
  --clean-md NDLR_MIDI.cleaned.md \
  --debug
```

The cleaned Markdown is useful if your source spec is messy or inconsistent.

---

## Markdown Format

Each Markdown file should consist of:

- Section headers (`## Pad`, `## Drone`, etc.)
- Followed by **Markdown tables**

### Required table columns

| Column        | Description |
|---------------|-------------|
| **CC (Hex)**  | MIDI CC number in hexadecimal (`0x10`). You may also use `CC` with decimal values. |
| **Target**    | Label shown on the Electra One control |
| **Range**     | Numeric range (e.g. `0–127`) |
| **Choices**   | For lists/buttons: comma-separated labels. If needed, specify values in parentheses (`Minor(2)`) |
| **Color**     | RGB hex color (e.g. `#FF8800`). Persists until changed |

### Layout notes

- Blank rows in tables create **blank spaces** in the Electra layout
- Color values persist until overridden
- Section boundaries define logical control groupings

See the `specs/` directory for complete, working examples.

---

## Current Limitations

- Only **7-bit CC** messages supported  
  (no NRPN or SysEx yet)
- **One-way output only**  
  (does not read or sync from instruments)
- Supported control types:
  - Faders
  - Lists
  - Buttons

---

## Contributing

Contributions are welcome!

- New Markdown specs
- Bug reports
- Improvements to layout rules or parsing

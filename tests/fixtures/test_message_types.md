# Test Message Types

## CC7 Controls (7-bit, default)

| CC | Label | Range | Description |
|----|-------|-------|-------------|
| 10 | Volume | 0-127 | Standard 7-bit CC |
| C20 | Pan | 0-127 | Explicit C prefix |

## CC14 Controls (14-bit, inferred from range)

| CC | Label | Range | Description |
|----|-------|-------|-------------|
| 30 | Fine Tune | 0-16383 | 14-bit CC inferred from range |
| C40 | Master Volume | 0-16383 | Explicit C prefix with 14-bit range |

## NRPN Controls

| CC | Label | Range | Description |
|----|-------|-------|-------------|
| N:100 | Filter Cutoff | 0-127 | 7-bit NRPN |
| N:200 | Resonance | 0-16383 | 14-bit NRPN |

## Program Controls

| CC | Label | Range | Description |
|----|-------|-------|-------------|
| P | PROGRAM | 0-127 | Program change |
| P | Bank Select | 0-99 | Program with custom range |

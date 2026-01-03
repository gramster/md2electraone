---
name: NDLR
channel: 15
groups: highlighted
---

# NDLR

## Setup

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| 21 | Drone Port | 1-7 | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B | #F54927 |
| 19 | Pad Port | 1-7 | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B | #6CF527 |
| 23 | Motif1 Port | 1-7 | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B | #27D3F5 |
| 24 | Motif2 Port | 1-7 | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B | #B027F5 |
| 89 | Load Seq | 1-5 |  | #C30D71 |
| 56 | KB Trans | 1-16 |  | #0D16C3 |
| 20 | Drone Chan | 1-16 |  | #F54927 |
| 18 | Pad Chan | 1-16 |  | #6CF527 |
| 22 | Motif1 Chan | 1-16 |  | #27D3F5 |
| 24 | Motif2 Chan | 1-16 |  | #B027F5 |
| 73 | Key | 1-12 | C, G, D, A, E, B, F#, Db, Ab, Eb, Bb, F | #BA0DC3 |
| 74 | Mode | 1-15 | Major, Dorian, Phrygian, Lydian, Mixolydian, Minor (Aeolian), Locrian, Gypsy Min, Harmonic Minor, Minor Pentatonic, Whole Tone, Tonic 2nds, Tonic 3rds, Tonic 4ths, Tonic 6ths | #BA0DC3 |

## Perform

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| PLAY/PAUSE | PLAY/PAUSE | 0 | | #8BF00F |
| 90 | PLAY/PAUSE: All | 0-63 | 0=Off, 63=On | #8BF00F |
| 4 | PLAY/PAUSE: Tempo | 5-127 |  | #4BF000 |
| 86 | PLAY/PAUSE: Drone | 0-63 | 0=Off, 63=On | #F54927 |
| 85 | PLAY/PAUSE: Pad | 0-63 | 0=Off, 63=On | #6CF527 |
| 87 | PLAY/PAUSE: Motif 1 | 0-63 | 0=Off, 63=On | #27D3F5 |
| CHORD | CHORD | 0 | | #BA0DC3 |
| 88 | PLAY/PAUSE: Motif 2 | 0-63 | 0=Off, 63=On | #B027F5 |
| 26 | CHORD: Degree | 1-7 | I, II, III, IV, V, VI, VII | #BA0DC3 |
| DRONE | DRONE | 0 | | #F54927 |
| 27 | CHORD: Type | 1-7 | Triad, 7th, sus2, alt1, alt2, sus4, 6th | #BA0DC3 |
| 69 | CHORD: Invert | 0-63 | 0=Off, 63=On | #BA0DC3 |
| PAD | PAD | 0 | | #6CF527 |
| 32 | DRONE: Position | 1-5 |  | #F54927 |
| 33 | DRONE: Type | 1-7 |  | #F54927 |
| 34 | DRONE: Trig | 1-8 |  | #F54927 |
| 28 | PAD: Position | 1-100 |  | #6CF527 |
| 29 | PAD: Strum | 1-7 | None, 1/32, 1/16, 1/8T, 3+1/8T, 1/8, & 3+1/8 | #6CF527 |
| MOTIF 1 | MOTIF 1 | 0 | | #27D3F5 |
| 30 | PAD: Range | 1-100 |  | #6CF527 |
| 31 | PAD: Spread | 1-6 |  | #6CF527 |
| MOTIF 2 | MOTIF 2 | 0 | | #B027F5 |
| 63 | PAD: Velocity | 1-127 |  | #6CF527 |
| 59 | PAD: Humanize | 0-10 | Off, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, 100% | #0D16C3 |
| 35 | MOTIF 1: Octave | 1-10 |  | #27D3F5 |
| 36 | MOTIF 1: Patt Len | 1-16 |  | #27D3F5 |
| 37 | MOTIF 1: Variation | 1-6 | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random | #27D3F5 |
| 43 | MOTIF 2: Octave | 1-10 |  | #B027F5 |
| 44 | MOTIF 2: Patt Len | 1-16 |  | #B027F5 |
| 45 | MOTIF 2: Variation | 1-6 | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random | #B027F5 |
| 38 | MOTIF 1: Pattern | 1-40 |  | #27D3F5 |
| 39 | MOTIF 1: Clk Div | 1-6 | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T | #27D3F5 |
| 40 | MOTIF 1: Rhythm Len | 4-32 |  | #27D3F5 |
| 46 | MOTIF 2: Pattern | 1-40 |  | #B027F5 |
| 47 | MOTIF 2: Clk Div | 1-6 | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T | #B027F5 |
| 48 | MOTIF 2: Rhythm Len | 4-32 |  | #B027F5 |
| 41 | MOTIF 1: Accent | 1-10 |  | #27D3F5 |
| 42 | MOTIF 1: Rhythm | 1-40 |  | #27D3F5 |
| 80 | MOTIF 1: Velocity | 1-127 |  | #27D3F5 |
| 49 | MOTIF 2: Accent | 1-10 |  | #B027F5 |
| 50 | MOTIF 2: Rhythm | 1-40 |  | #B027F5 |
| 84 | MOTIF 2: Velocity | 1-127 |  | #B027F5 |

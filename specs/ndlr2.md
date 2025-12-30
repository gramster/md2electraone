---
manufacturer: Conductive Labs
device: NDLR
port: 15
---

# NDLR

## Setup

| CC (Hex) | Color  | Target       | Range | Choices                                                 |
| -------- | ------ | ------------ | ----- | ------------------------------------------------------- |
| 0x15     | F54927 | Drone Chan   | 1-16  |                                                         |
| 0x13     | 6CF527 | Pad Chan     | 1-16  |                                                         |
| 0x17     | 27D3F5 | Motif1 Chan  | 1-16  |                                                         |
| 0x19     | B027F5 | Motif2 Chan  | 1-16  |                                                         |
| 0x59     | C30D71 | Load Seq     | 1-5   |                                                         |
| 0x38     | 0D16C3 | KB Trans     | 1-16  |                                                         |
| 0x14     | F54927 | Drone Port   | 1-7   | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x12     | 6CF527 | Pad Port     | 1-7   | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x16     | 27D3F5| Motif1 Port   | 1-7    | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B          |
| 0x18     | B027F5 | Motif2 Port  | 1-7   | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x49     | BA0DC3 | Key          | 1-12  | C, G, D, A, E, B, F#, Db, Ab, Eb, Bb, F                 |
| 0x4A     | BA0DC3 | Mode         | 1-15  | Major, Dorian, Phrygian, Lydian, Mixolydian, Minor (Aeolian), Locrian, Gypsy Min, Harmonic Minor, Minor Pentatonic, Whole Tone, Tonic 2nds, Tnic 3rds, Tonic 4ths, Tonic 6ths |

## Perform

| CC (Hex) | Color   | Target       | Range | Choices                                                    |
| -------- | ------- | ------------ | ----- | ---------------------------------------------------------- |
| 0x5A     | 8BF00F | All On        | 0-127 | Pause (0), Play (63)                                       |
| 0x44     | F54927 | Drone On      | 0-127 | Off (0), On (63)                                           |
| 0x43     | 6CF527 | Pad On        | 0-127 | Off (0), On (63)                                           |
| 0x53     | 27D3F5 | M1 On         | 0-127 | Off (0), On (63)                                           |
| 0x57     | B027F5 | M2 On         | 0-127 | Off (0), On (63)                                           |
| 0x3B     | 0D16C3 | Humanize      | 0-10  | Off (0), 10% (1), 20% (2), 30% (3), 40% (4), 50% (5), 60% (6), 70% (7), 80% (8), 90% (9), 100% (10) |
| 0x1A     | BA0DC3 | Chord Deg     | 1-7   | I, II, III, IV, V, VI, VII                                 |
| 0x1B     |        | Chord Type    | 1-7   | Triad, 7th, sus2, alt1, alt2, sus4, 6th                    |
| 0x45     |        | Chord Inv     | 0-127 | On (0), Off (63)                                           |
| 0x20     | F54927 | Drone Octv    | 1-5   |                                                            |
| 0x21     |        | Drone Notes   | 1-7   |                                                            |
| 0x22     |        | Drone Trig    | 1-8   |                                                            |
| 0x1C     | 6CF527 | Pad Position  | 1-100 |                                                            |
| 0x1D     |        | Pad Strum     | 1-7   | None, 1/32, 1/16, 1/8T, 3+1/8T, 1/8, & 3+1/8               |
| 0x1E     |        | Pad Range     | 1-100 |                                                            |
| 0x1F     |        | Pad Spread    | 1-6   |                                                            |
| 0x3F              | Pad Velocity  | 1-127 |                                                            |
| 0x23     | 27D3F5 | M1 Octave     | 1-10  |                                                            |
| 0x24     |        | M1 Patt Len   | 1-16  |                                                            |
| 0x25     |        | M1 Variation  | 1-6   | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random |
| 0x2B     | B027F5 | M2 Octave     | 1-10  |                                                            |
| 0x2C     |        | M2 Patt Len   | 1-16  |                                                            |
| 0x2D     |        | M2 Variation  | 1-6   | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random |
| 0x26     | 27D3F5 | M1 Pattern    | 1-40  |                                                            |
| 0x27     |        | M1 Clk Div    | 1-6   | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T                             |
| 0x28     |        | M1 Rhythm Len | 4-32  |                                                            |
| 0x2E     | B027F5 | M2 Pattern    | 1-40  |                                                            |
| 0x2F     |        | M2 Clk Div    | 1-6   | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T                             |
| 0x30     |        | M2 Rhythm Len | 4-32  |                                                            |
| 0x29     | 27D3F5 | M1 Accent     | 1-10  |                                                            |
| 0x2A     |        | M1 Rhythm     | 1-40  |                                                            |
| 0x50     |        | M1 Velocity   | 1-127 |                                                            |
| 0x31     | B027F5 | M2 Accent     | 1-10  |                                                            |
| 0x32     |        | M2 Rhythm     | 1-40  |                                                            |
| 0x54     |        | M2 Velocity   | 1-127 |                                                            |


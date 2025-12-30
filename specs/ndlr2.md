# NDLR

---
manufacturer: Conductive Labs
device: NDLR
port: 15
---

## Setup

| CC (Hex) | Target       | Range     | Choices                                                 |
| -------- | ------------ | --------- | ------------------------------------------------------- |
| 0x15     | Drone Chan   | 1-16      |                                                         |
| 0x14     | Drone Port   | 1-7       | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x13     | Pad Chan     | 1-16      |                                                         |
| 0x12     | Pad Port     | 1-7       | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x17     | Motif1 Chan  | 1-16      |                                                         |
| 0x16     | Motif1 Port  | 1-7       | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x19     | Motif2 Chan  | 1-16      |                                                         |
| 0x18     | Motif2 Port  | 1-7       | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x59     | Load Seq     | 1-5       |                                                         |
| 0x38     | KB Trans     | 1-16      |                                                         |
| 0x5A     | ALL Play     | 0-127     | Pause (0), Play (63)                                    |

## Perform

| CC (Hex) | Target        | Range | Choices                                                    |
| -------- | ------------- | ----- | ---------------------------------------------------------- |
| 0x1A     | Chord Deg     | 1-7   | I, II, III, IV, V, VI, VII                                 |
| 0x1B     | Chord Type    | 1-7   | Triad, 7th, sus2, alt1, alt2, sus4, 6th                    |
| 0x45     | Chord Inv     | 0-127 | On (0), Off (63)                                           |
| 0x49     | Key           | 1-12  | C, G, D, A, E, B, F#, Db, Ab, Eb, Bb, F                    |
| 0x4A     | Mode          | 1-15  | Major, Dorian, Phrygian, Lydian, Mixolydian, Minor (Aeolian), Locrian, Gypsy Min, Harmonic Minor, Minor Pentatonic, Whole Tone, Tonic 2nds, Tonic 3rds, Tonic 4ths, Tonic 6ths |
| 0x3B     | Humanize      | 0-10  | Off (0), 10% (1), 20% (2), 30% (3), 40% (4), 50% (5), 60% (6), 70% (7), 80% (8), 90% (9), 100% (10) |
| 0x20     | Drone Octave  | 1-5   |                                                            |
| 0x21     | Drone Notes   | 1-7   |                                                            |
| 0x22     | Drone Trig    | 1-8   |                                                            |
| 0x44     | Drone On      | 0-127 | Off (0), On (63)                                           |
| 0x1C     | Pad Position  | 1-100 |                                                            |
| 0x1D     | Pad Strum     | 1-7   | None, 1/32, 1/16, 1/8T, 3+1/8T, 1/8, & 3+1/8               |
| 0x1E     | Pad Range     | 1-100 |                                                            |
| 0x1F     | Pad Spread    | 1-6   |                                                            |
| 0x3F     | Pad Velocity  | 1-127 |                                                            |
| 0x43     | Pad On        | 0-127 | Off (0), On (63)                                           |
| 0x23     | M1 Octave     | 1-10  |                                                            |
| 0x24     | M1 Patt Len   | 1-16  |                                                            |
| 0x25     | M1 Variation  | 1-6   | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random |
| 0x26     | M1 Pattern    | 1-40  |                                                            |
| 0x27     | M1 Clk Div    | 1-6   | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T                             |
| 0x28     | M1 Rhythm Len | 4-32  |                                                            |
| 0x29     | M1 Accent     | 1-10  |                                                            |
| 0x2A     | M1 Rhythm     | 1-40  |                                                            |
| 0x50     | M1 Velocity   | 1-127 |                                                            |
| 0x53     | M1 On         | 0-127 | Off = 0-62, On = 63-127                                    |
| 0x2B     | M2 Octave     | 1-10  |                                                            |
| 0x2C     | M2 Patt Len   | 1-16  |                                                            |
| 0x2D     | M2 Variation  | 1-6   | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random |
| 0x2E     | M2 Pattern    | 1-40  |                                                            |
| 0x2F     | M2 Clk Div    | 1-6   | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T                             |
| 0x30     | M2 Rhythm Len | 4-32  |                                                            |
| 0x31     | M2 Accent     | 1-10  |                                                            |
| 0x32     | M2 Rhythm     | 1-40  |                                                            |
| 0x54     | M2 Velocity   | 1-127 |                                                            |
| 0x57     | M2 On         | 0-127 | Off (0), On (63)                                           |

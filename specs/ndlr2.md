---
manufacturer: Conductive Labs
device: NDLR
port: 1
channel: 15
version: 2
---

# NDLR

## Setup

| CC (Hex) | Color  | Target       | Range | Choices                                                 |
| -------- | ------ | ------------ | ----- | ------------------------------------------------------- |
| 0x15     | F54927 | Drone Port   | 1-7   | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x13     | 6CF527 | Pad Port     | 1-7   | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x17     | 27D3F5 | Motif1 Port  | 1-7   | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x18     | B027F5 | Motif2 Port  | 1-7   | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B           |
| 0x59     | C30D71 | Load Seq     | 1-5   |                                                         |
| 0x38     | 0D16C3 | KB Trans     | 1-16  |                                                         |
| 0x14     | F54927 | Drone Chan   | 1-16  |                                                         |
| 0x12     | 6CF527 | Pad Chan     | 1-16  |                                                         |
| 0x16     | 27D3F5 | Motif1 Chan  | 1-16  |                                                         |
| 0x18     | B027F5 | Motif2 Chan  | 1-16  |                                                         |
| 0x49     | BA0DC3 | Key          | 1-12  | C, G, D, A, E, B, F#, Db, Ab, Eb, Bb, F                 |
| 0x4A     | BA0DC3 | Mode         | 1-15  | Major, Dorian, Phrygian, Lydian, Mixolydian, Minor (Aeolian), Locrian, Gypsy Min, Harmonic Minor, Minor Pentatonic, Whole Tone, Tonic 2nds, Tonic 3rds, Tonic 4ths, Tonic 6ths |

## Perform

| CC (Hex) | Color  | Target        | Range | Choices                                                    |
| -------- | ------ | ------------- | ----- | ---------------------------------------------------------- |
| GROUP    | 8BF00F | PLAY/PAUSE    | 6     |                                                            |
| 0x5A     | 8BF00F | All           | 0-127 | Pause (0), Play (63)                                       |
| 0x4      | 4BF000 | Tempo         | 5-127 |                                                            |
| 0x56     | F54927 | Drone         | 0-127 | Off (0), On (63)                                           |
| 0x55     | 6CF527 | Pad           | 0-127 | Off (0), On (63)                                           |
| 0x57     | 27D3F5 | Motif 1       | 0-127 | Off (0), On (63)                                           |
| 0x58     | B027F5 | Motif 2       | 0-127 | Off (0), On (63)                                           |
| 0x1A     | BA0DC3 | Chord Deg     | 1-7   | I, II, III, IV, V, VI, VII                                 |
| 0x1B     |        | Chord Type    | 1-7   | Triad, 7th, sus2, alt1, alt2, sus4, 6th                    |
| 0x45     |        | Chord Inv     | 0-127 | On (0), Off (63)                                           |
| Group    | F54927 | DRONE         | 3     |                                                            |
| 0x20     | F54927 | Position      | 1-5   |                                                            |
| 0x21     |        | Type          | 1-7   |                                                            |
| 0x22     |        | Trig          | 1-8   |                                                            |
| Group    | 6CF527 | PAD           | 6     |                                                            |
| 0x1C     | 6CF527 | Position      | 1-100 |                                                            |
| 0x1D     |        | Strum         | 1-7   | None, 1/32, 1/16, 1/8T, 3+1/8T, 1/8, & 3+1/8               |
| 0x1E     |        | Range         | 1-100 |                                                            |
| 0x1F     |        | Spread        | 1-6   |                                                            |
| 0x3F     |        | Velocity      | 1-127 |                                                            |
| 0x3B     | 0D16C3 | Humanize      | 0-10  | Off (0), 10% (1), 20% (2), 30% (3), 40% (4), 50% (5), 60% (6), 70% (7), 80% (8), 90% (9), 100% (10) |
| Group    | 27D3F5 | MOTIF 1       | 3     |                                                            |
| 0x23     | 27D3F5 | Octave        | 1-10  |                                                            |
| 0x24     |        | Patt Len      | 1-16  |                                                            |
| 0x25     |        | Variation     | 1-6   | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random |
| Group    | B027F5 | MOTIF 2       | 3     |                                                            |
| 0x2B     | B027F5 | Octave        | 1-10  |                                                            |
| 0x2C     |        | Patt Len      | 1-16  |                                                            |
| 0x2D     |        | Variation     | 1-6   | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random |
| 0x26     | 27D3F5 | Pattern       | 1-40  |                                                            |
| 0x27     |        | Clk Div       | 1-6   | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T                             |
| 0x28     |        | Rhythm Len    | 4-32  |                                                            |
| 0x2E     | B027F5 | Pattern       | 1-40  |                                                            |
| 0x2F     |        | Clk Div       | 1-6   | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T                             |
| 0x30     |        | Rhythm Len    | 4-32  |                                                            |
| 0x29     | 27D3F5 | Accent        | 1-10  |                                                            |
| 0x2A     |        | Rhythm        | 1-40  |                                                            |
| 0x50     |        | Velocity      | 1-127 |                                                            |
| 0x31     | B027F5 | Accent        | 1-10  |                                                            |
| 0x32     |        | Rhythm        | 1-40  |                                                            |
| 0x54     |        | Velocity      | 1-127 |                                                            |


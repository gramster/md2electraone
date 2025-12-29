# NDLR


## Main

| CC (Hex) | Target           | Range | Choices                                                                                                                                         |
| -------- | ---------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0x1A     | Chord Degree     | 1-7   | I, II, III, IV, V, VI, VII                                                                                                                                                     |
| 0x1B     | Chord Type       | 1-7   | Triad, 7th, sus2, alt1, alt2, sus4, 6th                                                                                                                                        |
| 0x59     | Load Chord Seq | 1-5   |                                                                                                                                                                                |
| 0x45     | Inversion  | 0-127 | On (0), Off (63)                                                                                                                                                               |
| 0x49     | Key              | 1-12  | C, G, D, A, E, B, F#, Db, Ab, Eb, Bb, F                                                                                                                                        |
| 0x4A     | Mode / Scale     | 0-15  | Major, Dorian, Phrygian, Lydian, Mixolydian, Minor (Aeolian), Locrian, Gypsy Min, Harmonic Minor, Minor Pentatonic, Whole Tone, Tonic 2nds, Tonic 3rds, Tonic 4ths, Tonic 6ths |
| 0x3B     | Humanize         | 0-10  | 0 (off), 1-10 (10%-100%)                                                                                                                                                       |
| 0x38     | Transpose     | 1-16  |                                                                                                                                                                                |
| 0x5A     | ALL Play | 0-127 | Pause (0), Play (63)                                                                                                                                                           |

## Drone

| **CC (Hex)** | **Target**   | **Range** | **Choices**                                   |
| ------------ | ------------ | --------- | --------------------------------------------- |
| 0x15         | Channel      | 1-16      |                                               |
| 0x14         | Port         | 1-7       | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B |
| 0x20         | Octave       | 1-5       |                                               |
| 0x21         | Notes        | 1-7       |                                               |
| 0x22         | Trigger      | 1-8       |                                               |
| 0x44         | On/Off       | 0-127     | Off (0), On (63)                              |


## Pad

| **CC (Hex)** | **Target**   | **Range** | **Choices**                                   |
| ------------ | ------------ | --------- | --------------------------------------------- |
| 0x13         | Channel      | 1-16      |                                               |
| 0x12         | Port         | 1-7       | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B |
| 0x1C         | Position     | 1-100     |                                               |
| 0x1D         | Strum        | 1-7       | None, 1/32, 1/16, 1/8T, 3+1/8T, 1/8, & 3+1/8  |
| 0x1E         | Range        | 1-100     |                                               |
| 0x1F         | Spread       | 1-6       |                                               |
| 0x3F         | Velocity     | 1-127     |                                               |
| 0x43         | On/Off       | 0-127     | Off (0), On (63)                              |


## Motif 1

| **CC (Hex)** | **Target**   | **Range** | **Choices**                                                |
| ------------ | ------------ | --------- | ---------------------------------------------------------- |
| 0x17         | Channel      | 1-16      |                                                            |
| 0x16         | Port         | 1-7       | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B              |
| 0x23         | Octave       | 1-10      |                                                            |
| 0x24         | Pattern Len  | 1-16      |                                                            |
| 0x25         | Variation    | 1-6       | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random |
| 0x26         | Pattern      | 1-40      |                                                            |
| 0x27         | Clock Div    | 1-6       | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T                             |
| 0x28         | Rhythm Len   | 4-32      |                                                            |
| 0x29         | Accent       | 1-10      |                                                            |
| 0x2A         | Rhythm       | 1-40      |                                                            |
| 0x50         | Velocity     | 1-127     |                                                            |
| 0x53         | On/Off       | 0-127     | Off (0), On (63)                                           |


## Motif 2


| **CC (Hex)** | **Target**   | **Range** | **Choices**                                                |
| ------------ | ------------ | --------- | ---------------------------------------------------------- |
| 0x19         | Channel      | 1-16      |                                                            |
| 0x18         | Port         | 1-7       | All, USB 1, USB 2, USB 3, USB 4, DIN A, DIN B              |
| 0x2B         | Octave       | 1-10      |                                                            |
| 0x2C         | Pattern Len  | 1-16      |                                                            |
| 0x2D         | Variation    | 1-6       | Forward, Backward, Ping-Pong, Ping-Pong2, Odd/Even, Random |
| 0x2E         | Pattern      | 1-40      |                                                            |
| 0x2F         | Clock Div    | 1-6       | 1/1, 1/2, 1/4, 1/8, 1/3T, 1/6T                             |
| 0x30         | Rhythm Len   | 4-32      |                                                            |
| 0x31         | Accent       | 1-10      |                                                            |
| 0x32         | Rhythm       | 1-40      |                                                            |
| 0x54         | Velocity     | 1-127     |                                                            |
| 0x57         | On/Off       | 0-127     | Off (0), On (63)                                           |

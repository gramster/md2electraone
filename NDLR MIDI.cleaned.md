# NDLR

## Main

| CC | Label          | Range | Choices                                                                                                                                                                                                                          |
| -- | -------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 26 | Chord Degree   | 1-7   | I(1), II(2), III(3), IV(4), V(5), VI(6), VII(7)                                                                                                                                                                                  |
| 27 | Chord Type     | 1-7   | Triad(1), 7th(2), sus2(3), alt1(4), alt2(5), sus4(6), 6th(7)                                                                                                                                                                     |
| 89 | Load Chord Seq | 1-5   |                                                                                                                                                                                                                                  |
| 69 | Inversion      | 0-127 | On(0), Off(63)                                                                                                                                                                                                                   |
| 73 | Key            | 1-12  | C(1), G(2), D(3), A(4), E(5), B(6), F#(7), Db(8), Ab(9), Eb(10), Bb(11), F(12)                                                                                                                                                   |
| 74 | Mode / Scale   | 0-15  | Major(0), Dorian(1), Phrygian(2), Lydian(3), Mixolydian(4), Minor (Aeolian)(5), Locrian(6), Gypsy Min(7), Harmonic Minor(8), Minor Pentatonic(9), Whole Tone(10), Tonic 2nds(11), Tonic 3rds(12), Tonic 4ths(13), Tonic 6ths(14) |
| 59 | Humanize       | 0-10  | 0 (off)(0), 1-10 (10%-100%)(1)                                                                                                                                                                                                   |
| 56 | Transpose      | 1-16  |                                                                                                                                                                                                                                  |
| 90 | ALL Play       | 0-127 | Pause(0), Play(63)                                                                                                                                                                                                               |

## Drone

| CC | Label   | Range | Choices                                                            |
| -- | ------- | ----- | ------------------------------------------------------------------ |
| 21 | Channel | 1-16  |                                                                    |
| 20 | Port    | 1-7   | All(1), USB 1(2), USB 2(3), USB 3(4), USB 4(5), DIN A(6), DIN B(7) |
| 32 | Octave  | 1-5   |                                                                    |
| 33 | Notes   | 1-7   |                                                                    |
| 34 | Trigger | 1-8   |                                                                    |
| 68 | On/Off  | 0-127 | Off(0), On(63)                                                     |

## Pad

| CC | Label    | Range | Choices                                                            |
| -- | -------- | ----- | ------------------------------------------------------------------ |
| 19 | Channel  | 1-16  |                                                                    |
| 18 | Port     | 1-7   | All(1), USB 1(2), USB 2(3), USB 3(4), USB 4(5), DIN A(6), DIN B(7) |
| 28 | Position | 1-100 |                                                                    |
| 29 | Strum    | 1-7   | None(1), 1/32(2), 1/16(3), 1/8T(4), 3+1/8T(5), 1/8(6), & 3+1/8(7)  |
| 30 | Range    | 1-100 |                                                                    |
| 31 | Spread   | 1-6   |                                                                    |
| 63 | Velocity | 1-127 |                                                                    |
| 67 | On/Off   | 0-127 | Off(0), On(63)                                                     |

## Motif 1

| CC | Label       | Range | Choices                                                                      |
| -- | ----------- | ----- | ---------------------------------------------------------------------------- |
| 23 | Channel     | 1-16  |                                                                              |
| 22 | Port        | 1-7   | All(1), USB 1(2), USB 2(3), USB 3(4), USB 4(5), DIN A(6), DIN B(7)           |
| 35 | Octave      | 1-10  |                                                                              |
| 36 | Pattern Len | 1-16  |                                                                              |
| 37 | Variation   | 1-6   | Forward(1), Backward(2), Ping-Pong(3), Ping-Pong2(4), Odd/Even(5), Random(6) |
| 38 | Pattern     | 1-40  |                                                                              |
| 39 | Clock Div   | 1-6   | 1/1(1), 1/2(2), 1/4(3), 1/8(4), 1/3T(5), 1/6T(6)                             |
| 40 | Rhythm Len  | 4-32  |                                                                              |
| 41 | Accent      | 1-10  |                                                                              |
| 42 | Rhythm      | 1-40  |                                                                              |
| 80 | Velocity    | 1-127 |                                                                              |
| 83 | On/Off      | 0-127 | Off(0), On(63)                                                               |

## Motif 2

| CC | Label       | Range | Choices                                                                      |
| -- | ----------- | ----- | ---------------------------------------------------------------------------- |
| 25 | Channel     | 1-16  |                                                                              |
| 24 | Port        | 1-7   | All(1), USB 1(2), USB 2(3), USB 3(4), USB 4(5), DIN A(6), DIN B(7)           |
| 43 | Octave      | 1-10  |                                                                              |
| 44 | Pattern Len | 1-16  |                                                                              |
| 45 | Variation   | 1-6   | Forward(1), Backward(2), Ping-Pong(3), Ping-Pong2(4), Odd/Even(5), Random(6) |
| 46 | Pattern     | 1-40  |                                                                              |
| 47 | Clock Div   | 1-6   | 1/1(1), 1/2(2), 1/4(3), 1/8(4), 1/3T(5), 1/6T(6)                             |
| 48 | Rhythm Len  | 4-32  |                                                                              |
| 49 | Accent      | 1-10  |                                                                              |
| 50 | Rhythm      | 1-40  |                                                                              |
| 84 | Velocity    | 1-127 |                                                                              |
| 87 | On/Off      | 0-127 | Off(0), On(63)                                                               |

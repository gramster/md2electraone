---
devices:
  - name: Generic MIDI
  - port: 1
  - channel: 9
  - name: Generic MIDI
  - port: 1
  - channel: 10
---

# micromonsta 2

## A+B=synth

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| G:OSC 1 | OSC 1 | 1 | | #FFFFFF |
| 1:C:39 | OSC1 SHAPE  | 0-127 |  | #F49500 |
| G:OSC 2 | OSC 2 | 1 | | #FFFFFF |
| 1:C:42 | OSC2 SHAPE  | 0-127 |  | #F49500 |
| G:OSC 3 | OSC 3 | 1 | | #FFFFFF |
| 1:C:45 | OSC3 SHAPE  | 0-127 |  | #F49500 |
| G:OSC 1 A | OSC 1 | 1 | | #529DEC |
| 2:C:39 | OSC1 SHAPE  | 0-127 |  | #529DEC |
| G:OSC 2 A | OSC 2 | 1 | | #529DEC |
| 2:C:42 | OSC2 SHAPE  | 0-127 |  | #529DEC |
| G:OSC 3 A | OSC 3 | 1 | | #529DEC |
| 2:C:45 | OSC3 SHAPE  | 0-127 |  | #529DEC |
| G:OSC 1 B | OSC 1 | 1 | | #FFFFFF |
| 1:C:40 | OSC1 TUNE  | -25-12 |  | #F49500 |
| G:OSC 2 B | OSC 2 | 1 | | #FFFFFF |
| 1:C:43 | OSC2 TUNE  | -25-12 |  | #F49500 |
| G:OSC 3 B | OSC 3 | 1 | | #FFFFFF |
| 1:C:46 | OSC3 TUNE  | -25-12 |  | #F49500 |
| G:OSC 1 D | OSC 1 | 1 | | #FFFFFF |
| 2:C:40 | OSC1 TUNE  | -25-12 |  | #529DEC |
| G:OSC 2 D | OSC 2 | 1 | | #FFFFFF |
| 2:C:43 | OSC2 TUNE  | -25-12 |  | #529DEC |
| G:OSC 3 D | OSC 3 | 1 | | #FFFFFF |
| 2:C:46 | OSC3 TUNE  | -25-12 |  | #529DEC |
| G:OSC 1 C | OSC 1 | 1 | | #FFFFFF |
| 1:C:41 | OSC1 FINE TUNE | -26-25 |  | #F49500 |
| G:OSC 2 C | OSC 2 | 1 | | #FFFFFF |
| 1:C:44 | OSC2 FINE TUNE | -26-25 |  | #F49500 |
| G:OSC 3 C | OSC 3 | 1 | | #FFFFFF |
| 1:C:47 | OSC3 FINE TUNE | -26-25 |  | #F49500 |
| G:OSC 1 E | OSC 1 | 1 | | #FFFFFF |
| 2:C:41 | OSC1 FINE TUNE | -26-25 |  | #529DEC |
| G:OSC 2 E | OSC 2 | 1 | | #FFFFFF |
| 2:C:44 | OSC2 FINE TUNE | -26-25 |  | #529DEC |
| G:OSC 3 E | OSC 3 | 1 | | #FFFFFF |
| 2:C:47 | OSC3 FINE TUNE | -26-25 |  | #529DEC |
| G:LEVELS | LEVELS | 3 | | #FFFFFF |
| 1:C:48 | OSC1 LEVEL | 0-127 |  | #F49500 |
| 1:C:49 | OSC2 LEVEL | 0-127 |  | #F49500 |
| 1:C:50 | OSC3 LEVEL | 0-127 |  | #F49500 |
| G:LEVELS A | LEVELS | 3 | | #FFFFFF |
| 2:C:48 | OSC1 LEVEL | 0-127 |  | #529DEC |
| 2:C:49 | OSC2 LEVEL | 0-127 |  | #529DEC |
| 2:C:50 | OSC3 LEVEL | 0-127 |  | #529DEC |
| G:AMP ENV 1 | AMP ENV 1 | 1 | | #FFFFFF |
| 1:C:73,75,79,72 | ENV 1 | 0-127 | ADSR | #FFFFFF |
| G:FILT ENV 2 | FILT ENV 2 | 1 | | #FFFFFF |
| 1:C:80,81,82,83 | ENV 2 | 0-127 | ADSR | #FFFFFF |
| G:ENV 3 | ENV 3 | 1 | | #FFFFFF |
| 1:C:84,85,86,87 | ENV 3 | 0-127 | ADSR | #FFFFFF |
| G:AMP ENV 1 A | AMP ENV 1 | 1 | | #529DEC |
| 2:C:73,75,79,72 | ENV 1 | 0-127 | ADSR | #FFFFFF |
| G:FILT ENV 2 A | FILT ENV 2 | 1 | | #529DEC |
| 2:C:80,81,82,83 | ENV 2 | 0-127 | ADSR | #FFFFFF |
| G:ENV 3 A | ENV 3 | 1 | | #529DEC |
| 2:C:84,85,86,87 | ENV 3 | 0-127 | ADSR | #FFFFFF |
| G:FILTER | FILTER | 3 | | #C44795 |
| 1:C:74 | CUT OFF | 0-255 |  | #C44795 |
| 1:C:71 | RESO | 0-127 |  | #C44795 |
| 1:C:88 | FLTR ENV | -100-99 |  | #FFFFFF |
| G:FILTER A | FILTER | 3 | | #F49500 |
| 2:C:74 | CUT OFF | 0-255 |  | #F45C51 |
| 2:C:71 | RESO | 0-127 |  | #F45C51 |
| 2:C:88 | FLTR ENV | -100-99 |  | #529DEC |

## A+B=mods

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| G:GLIDE | GLIDE | 1 | | #F49500 |
| 1:C:5 | GLIDE | 0-127 |  | #F49500 |
| G:VEL | VEL | 2 | | #F49500 |
| 1:C:36 | VCA VEL SENS | 0-127 |  | #F49500 |
| 1:C:37 | FLTR VEL SENS | 0-127 |  | #F49500 |
| G:GLIDE A | GLIDE | 1 | | #C44795 |
| 2:C:5 | GLIDE | 0-127 |  | #C44795 |
| G:VEL A | VEL | 2 | | #C44795 |
| 2:C:36 | VCA VEL SENS | 0-127 |  | #C44795 |
| 2:C:37 | FLTR VEL SENS | 0-127 |  | #C44795 |
| G:DETUNE | DETUNE | 3 | | #FFFFFF |
| 1:C:33 | VOICE DETUNE | 0-127 |  | #F49500 |
| 1:C:34 | OSC DETUNE | 0-127 |  | #F49500 |
| 1:C:35 | PAN SPREAD | 0-127 |  | #F49500 |
| G:DETUNE A | DETUNE | 3 | | #C44795 |
| 2:C:33 | VOICE DETUNE | 0-127 |  | #C44795 |
| 2:C:34 | OSC DETUNE | 0-127 |  | #C44795 |
| 2:C:35 | PAN SPREAD | 0-127 |  | #C44795 |
| G:MODS LVL | MODS LVL | 3 | | #FFFFFF |
| 1:C:52 | MOD 1 | -100-99 |  | #FFFFFF |
| 1:C:53 | MOD 2 | -100-99 |  | #FFFFFF |
| 1:C:54 | MOD 3 | -100-99 |  | #FFFFFF |
| G:MODS LVL A | MODS LVL | 3 | | #529DEC |
| 2:C:52 | MOD 1 | -100-99 |  | #529DEC |
| 2:C:53 | MOD 2 | -100-99 |  | #529DEC |
| 2:C:54 | MOD 3 | -100-99 |  | #529DEC |
| G:MODS LVL B | MODS LVL | 3 | | #FFFFFF |
| 1:C:55 | MOD 4 | -100-99 |  | #FFFFFF |
| 1:C:56 | MOD 5 | -100-99 |  | #FFFFFF |
| 1:C:57 | MOD 6 | -100-99 |  | #FFFFFF |
| G:MODS LVL D | MODS LVL | 3 | | #FFFFFF |
| 2:C:55 | MOD 4 | -100-99 |  | #529DEC |
| 2:C:56 | MOD 5 | -100-99 |  | #529DEC |
| 2:C:57 | MOD 6 | -100-99 |  | #529DEC |
| G:MODS LVL C | MODS LVL | 3 | | #FFFFFF |
| 1:C:58 | MOD 7 | -100-99 |  | #FFFFFF |
| 1:C:59 | MOD 8 | -100-99 |  | #FFFFFF |
| 1:C:60 | MOD 9 | -100-99 |  | #FFFFFF |
| G:MODS LVL E | MODS LVL | 3 | | #FFFFFF |
| 2:C:58 | MOD 7 | -100-99 |  | #529DEC |
| 2:C:59 | MOD 8 | -100-99 |  | #529DEC |
| 2:C:60 | MOD 9 | -100-99 |  | #529DEC |
| G:MODS LVL F | MODS LVL | 1 | | #FFFFFF |
| 1:C:61 | MOD 10 | -100-99 |  | #FFFFFF |
| G:FLTR TRKG | FLTR TRKG | 1 | | #F49500 |
| 1:C:89 | FLTR TRACKING | 0-127 |  | #F49500 |
| G:MOD KNOB | MOD KNOB | 1 | | #03A598 |
| 1:C:70 | MOD KNOB | 0-127 |  | #03A598 |
| G:MODS LVL G | MODS LVL | 1 | | #FFFFFF |
| 2:C:61 | MOD 10 | -100-99 |  | #529DEC |
| G:FLTR TRKG A | FLTR TRKG | 1 | | #C44795 |
| 2:C:89 | FLTR TRACKING | 0-127 |  | #C44795 |
| G:MOD KNOB A | MOD KNOB | 1 | | #03A598 |
| 2:C:70 | MOD KNOB | 0-127 |  | #03A598 |

## misc

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| G:DELAY | DELAY | 3 | | #FFFFFF |
| 1:C:26 | DELAY TIME | 0-127 |  | #FFFFFF |
| 1:C:27 | DELAY FEEDBACK | 0-127 |  | #FFFFFF |
| 1:C:28 | DELAY LEVEL | 0-127 |  | #FFFFFF |
| G:DELAY A | DELAY | 3 | | #03A598 |
| 2:C:26 | DELAY TIME | 0-127 |  | #03A598 |
| 2:C:27 | DELAY FEEDBACK | 0-127 |  | #03A598 |
| 2:C:28 | DELAY LEVEL | 0-127 |  | #03A598 |
| G:REVERB | REVERB | 3 | | #FFFFFF |
| 1:C:29 | REVERB DECAY | 0-127 |  | #FFFFFF |
| 1:C:30 | REVERB MOD | 0-127 |  | #FFFFFF |
| 1:C:31 | REVERB LEVEL | 0-127 |  | #FFFFFF |
| G:MODS LVL H | MODS LVL | 3 | | #FFFFFF |
| 2:C:29 | REVERB DECAY | 0-127 |  | #03A598 |
| 2:C:30 | REVERB MOD | 0-127 |  | #03A598 |
| 2:C:31 | REVERB LEVEL | 0-127 |  | #03A598 |
| G:HARCH | HARCH | 2 | | #FFFFFF |
| 1:C:51 | NOISE LEVEL | 0-127 |  | #529DEC |
| 1:C:62 | LAG LEVEL | 0-127 |  | #529DEC |
|  |  |  |  |  |
| G:HARCH A | HARCH | 2 | | #FFFFFF |
| 2:C:51 | NOISE LEVEL | 0-127 |  | #F45C51 |
| 2:C:62 | LAG LEVEL | 0-127 |  | #F45C51 |
|  |  |  |  |  |
| 1:C:90 | FILTER FM | 0-127 |  | #529DEC |
| 1:C:91 | VOICE DRIVE | 0-127 |  | #529DEC |
|  |  |  |  |  |
| 2:C:90 | FILTER FM | 0-127 |  | #F45C51 |
| 2:C:91 | VOICE DRIVE | 0-127 |  | #F45C51 |
|  |  |  |  |  |
| G:LFO SPEED | LFO SPEED | 3 | | #FFFFFF |
| 1:C:76 | LFO1 SPEED | 0-127 |  | #F49500 |
| 1:C:77 | LFO2 SPEED | 0-127 |  | #F49500 |
| 1:C:78 | LFO3 SPEED | 0-127 |  | #F49500 |
| G:LFO SPEED A | LFO SPEED | 3 | | #FFFFFF |
| 2:C:76 | LFO1 SPEED | 0-127 |  | #C44795 |
| 2:C:77 | LFO2 SPEED | 0-127 |  | #C44795 |
| 2:C:78 | LFO3 SPEED | 0-127 |  | #C44795 |
| 1:P | PROGRAM | 0-127 |  | #FFFFFF |
|  |  |  |  |  |
|  |  |  |  |  |
| 2:P | PROGRAM | 0-127 |  | #FFFFFF |
|  |  |  |  |  |
|  |  |  |  |  |

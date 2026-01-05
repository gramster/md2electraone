---
name: Redshift 6
channel: 1
devices:
  device count: 6
  - name: Redshift 6 Part <device>
    port: 1
    channel: <device>
  - name: Redshift 6 Global
    port: 1
    channel: 15
groups: highlighted
---

# Redshift 6

## Effects

device: Redshift 6 Global

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| fx | FX |  | | #FF6B00 |
| N:1024 | fx: Enabled | 0-1 | Off, On | #FF6B00 |
| N:1025 | fx: Engine | 0-3 | Stage Reverb, X-Delay, Vintage Chorus, Chorus+ | #FF6B00 |
| | | | | |
| clock | CLOCK | | | #00A8FF |
| N:1280 | clock: BPM | 100-2500 | | #00A8FF |
| | | | | |
| | | | | |
| reverb | REVERB | | | #AA00FF |
| N:3968 | reverb: Decay | 0-16383 | | |
| N:3969 | reverb: Level | 0-16383 | | |
| delay | DELAY | | | #FF6B00 |
| N:4352 | delay: Time | 0-16383 | | |
| N:4353 | delay: BPM Div | 0-12 | 1/32, 1/16t, 1/32., 1/16, 1/8t, 1/16., 1/8, 1/4t, 1/8., 1/4, 1/2t, 1/4., 1/2 | |
| chorus | CHORUS | | | #00FFAA |
| N:4096 | chorus: Mode | 0-3 | Off, I, II, I + II | |
| N:4224 | chorus: Mix | 0-16383 | | |
| N:3970 | reverb: Damping | 0-16383 | | |
| N:3971 | reverb: Hi Cut | 0-16383 | | |
| N:4354 | delay: Level | 0-16383 | | |
| N:4355 | delay: Feedback | 0-16383 | | |
| N:4225 | chorus: Delay | 0-16383 | | |
| N:4226 | chorus: Depth | 0-16383 | | |
| N:3972 | reverb: Lo Cut | 0-16383 | |  |
| N:3973 | reverb: Predelay | 0-16383 | |  |
| N:4356 | delay: Sync | 0-1 | Off, On |  |
| N:4357 | delay: X-Pan | 0-16383 | |  |
| N:4227 | chorus: Rate | 0-16383 | |  |
| N:4228 | chorus: Feedback | 0-16383 | |  |
| N:3974 | reverb: Stage | 0-4 | Shower, Club, Arena, Canyon, Cosmos |  |
| N:3975 | reverb: Chorus | 0-3 | Off, I, II, I + II |  |
| N:4358 | delay: Time Offset | 0-16383 | |  |
| N:4359 | delay: Damping | 0-16383 | |  |
| N:4229 | chorus: Tone | 0-16383 | |  |
| N:4230 | chorus: Mode | 0-3 | SqrWide, SinWide, Sqr, Sin |  |
| | | | | |
| | | | | |
| N:4360 | delay: Chorus | 0-3 | Off, I, II, I + II |  |

## Part Settings A

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| part1 | PART 1 | | | #FFAA00 |
| part2 | PART 2 | | | #FF6600 |
| part3 | PART 3 | | | #FF0066 |
| part4 | PART 4 | | | #AA00FF |
| part5 | PART 5 | | | #00AAFF |
| part6 | PART 6 | | | #00FFAA |
| 1:7 | part1: Volume | 0-127 | | |
| 2:7 | part2: Volume | 0-127 | | |
| 3:7 | part3: Volume | 0-127 | | |
| 4:7 | part4: Volume | 0-127 | | |
| 5:7 | part5: Volume | 0-127 | | |
| 6:7 | part6: Volume | 0-127 | | |
| 1:N:769 | part1: Polyphony | 1-6 | | |
| 2:N:769 | part2: Polyphony | 1-6 | | |
| 3:N:769 | part3: Polyphony | 1-6 | | |
| 4:N:769 | part4: Polyphony | 1-6 | | |
| 5:N:769 | part5: Polyphony | 1-6 | | |
| 6:N:769 | part6: Polyphony | 1-6 | | |
| 1:N:770 | part1: Unison | 1-6 | | |
| 2:N:770 | part2: Unison | 1-6 | | |
| 3:N:770 | part3: Unison | 1-6 | | |
| 4:N:770 | part4: Unison | 1-6 | | |
| 5:N:770 | part5: Unison | 1-6 | | |
| 6:N:770 | part6: Unison | 1-6 | | |
| 1:N:771 | part1: Uni Pan Spread | 0-16383 | | |
| 2:N:771 | part2: Uni Pan Spread | 0-16383 | | |
| 3:N:771 | part3: Uni Pan Spread | 0-16383 | | |
| 4:N:771 | part4: Uni Pan Spread | 0-16383 | | |
| 5:N:771 | part5: Uni Pan Spread | 0-16383 | | |
| 6:N:771 | part6: Uni Pan Spread | 0-16383 | | |
| 1:N:772 | part1: Paraphony | 1-16 | | |
| 2:N:772 | part2: Paraphony | 1-16 | | |
| 3:N:772 | part3: Paraphony | 1-16 | | |
| 4:N:772 | part4: Paraphony | 1-16 | | |
| 5:N:772 | part5: Paraphony | 1-16 | | |
| 6:N:772 | part6: Paraphony | 1-16 | | |
| 1:N:773 | part1: Trigger Mode | 0-1 | Legato, Retrig | |
| 2:N:773 | part2: Trigger Mode | 0-1 | Legato, Retrig | |
| 3:N:773 | part3: Trigger Mode | 0-1 | Legato, Retrig | |
| 4:N:773 | part4: Trigger Mode | 0-1 | Legato, Retrig | |
| 5:N:773 | part5: Trigger Mode | 0-1 | Legato, Retrig | |
| 6:N:773 | part6: Trigger Mode | 0-1 | Legato, Retrig | |

## Part Settings B

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| part1 | PART 1 | | | #FFAA00 |
| part2 | PART 2 | | | #FF6600 |
| part3 | PART 3 | | | #FF0066 |
| part4 | PART 4 | | | #AA00FF |
| part5 | PART 5 | | | #00AAFF |
| part6 | PART 6 | | | #00FFAA |
| 1:N:774 | part1: Part Enabled | 0-1 | Off, On |  |
| 2:N:774 | part2: Part Enabled | 0-1 | Off, On |  |
| 3:N:774 | part3: Part Enabled | 0-1 | Off, On |  |
| 4:N:774 | part4: Part Enabled | 0-1 | Off, On |  |
| 5:N:774 | part5: Part Enabled | 0-1 | Off, On |  |
| 6:N:774 | part6: Part Enabled | 0-1 | Off, On |  |
| 1:N:775 | part1: Output | 0-2 | Main, Aux1, Aux2 |  |
| 2:N:775 | part2: Output | 0-2 | Main, Aux1, Aux2 |  |
| 3:N:775 | part3: Output | 0-2 | Main, Aux1, Aux2 |  |
| 4:N:775 | part4: Output | 0-2 | Main, Aux1, Aux2 |  |
| 5:N:775 | part5: Output | 0-2 | Main, Aux1, Aux2 |  |
| 6:N:775 | part6: Output | 0-2 | Main, Aux1, Aux2 |  |
| 1:N:776 | part1: Voices Mode | 0-1 | Dynamic, Reserve |  |
| 2:N:776 | part2: Voices Mode | 0-1 | Dynamic, Reserve |  |
| 3:N:776 | part3: Voices Mode | 0-1 | Dynamic, Reserve |  |
| 4:N:776 | part4: Voices Mode | 0-1 | Dynamic, Reserve |  |
| 5:N:776 | part5: Voices Mode | 0-1 | Dynamic, Reserve |  |
| 6:N:776 | part6: Voices Mode | 0-1 | Dynamic, Reserve |  |
| 1:N:1408 | part1: DCO Key Follow | 0-16383 | |  |
| 2:N:1408 | part2: DCO Key Follow | 0-16383 | |  |
| 3:N:1408 | part3: DCO Key Follow | 0-16383 | |  |
| 4:N:1408 | part4: DCO Key Follow | 0-16383 | |  |
| 5:N:1408 | part5: DCO Key Follow | 0-16383 | |  |
| 6:N:1408 | part6: DCO Key Follow | 0-16383 | |  |
| 1:N:1409 | part1: Lowest Key | 0-127 | |  |
| 2:N:1409 | part2: Lowest Key | 0-127 | |  |
| 3:N:1409 | part3: Lowest Key | 0-127 | |  |
| 4:N:1409 | part4: Lowest Key | 0-127 | |  |
| 5:N:1409 | part5: Lowest Key | 0-127 | |  |
| 6:N:1409 | part6: Lowest Key | 0-127 | |  |
| 1:N:1410 | part1: Highest Key | 0-127 | |  |
| 2:N:1410 | part2: Highest Key | 0-127 | |  |
| 3:N:1410 | part3: Highest Key | 0-127 | |  |
| 4:N:1410 | part4: Highest Key | 0-127 | |  |
| 5:N:1410 | part5: Highest Key | 0-127 | |  |
| 6:N:1410 | part6: Highest Key | 0-127 | |  |

## Part <device>: Waveform

device: Redshift 6 Part <device>

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| dco1 | DCO | 9 | | #00D4FF |
| N:128 | dco1: Osc 1 Wave | 0-4 | Saw, Pulse, Saw R, Pulse R, None | |
| N:129 | dco1: Osc 2 Wave | 0-4 | Saw, Pulse, Saw R, Pulse R, None | |
| N:130 | dco1: Osc 1 PW | 0-16383 | | |
| mirror1 | MIRROR TWINS | 3 | | #00FF88 |
| N:3840 | mirror1: Separation | 0-16383 | | |
| N:3841 | mirror1: Depth | 0-16383 | | |
| N:3842 | mirror1: Twin | 0-1 | Off, On | |
| N:131 | dco1: Osc 2 PW | 0-16383 | | |
| N:132 | dco1: Osc 2 Tune | 0-16383 | | |
| 75 | dco1: Stack | 1-8 | |  |
| amp1 | AMP | 3 | | #FFD000 |
| N:384 | amp1: Gain | 0-16383 | |  |
| 10 | amp1: Pan | 0-127 | |  |
| N:386 | amp1: Vel > Amp | 0-16383 | |  |
| 76 | dco1: Detune | 0-127 | |  |
| 77 | dco1: Balance | 0-127 | |  |
| N:136 | dco1: Noise Level | 0-16383 | |  |
| drive1 | DRIVE & CHARACTER | 2 | | #FF4400 |
| 78 | drive1: Drive | 0-127 | |  |
| 70 | drive1: Character | 0-127 | |  |
| | | | | |
| vcf1 | VCF | 7 | | #00FF88 |
| 79 | vcf1: Cutoff | 0-127 | |  |
| 71 | vcf1: Resonance | 0-127 | |  |
| 73 | vcf1: Env Amount | 0-127 | |  |
| envs1 | ENVELOPES | 8 | | #FF00DD |
| 14,2:15,2:16,2:17 | envs1: Amp | 0-127 | ADSR |  |
| N:2436 | envs1: Amp Reset | 0-1 | Off, On |  |
| 18,2:19,2:20,2:21 | envs1: VCF | 0-127 | ADSR |  |
| 72 | vcf1: Filter Mode | 0-127 | |  |
| N:260 | vcf1: Key Follow | 0-16383 | |  |
| N:261 | vcf1: Vel > VCF Env | 0-16383 | |  |
| N:2564 | envs1: VCF Reset | 0-1 | Off, On |  |
| N:2688,2:N:2689,2:N:2690,2:N:2691 | envs1: DCO | 0-16383 | ADSR |  |
| N:2692 | envs1: DCO Reset | 0-1 | Off, On |  |
| N:262 | vcf1: Filter Engine | 0-1 | Classic, Mirror Twins |  |
| | | | | |
| | | | | |
| N:2816,2:N:2817,2:N:2818,2:N:2819 | envs1: Aux | 0-16383 | ADSR |  |
| N:2820 | envs1: Aux Reset | 0-1 | Off, On |  |
| | | | | |


## Part <device>: LFOS

device: Redshift 6 Part <device>

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| lfo1-1 | LFO 1 | | | #FF5500 |
| N:2944 | lfo1-1: Rate | 0-16383 | | |
| N:2945 | lfo1-1: Clock Mult | 0-19 | 8/1, 4/1, 2/1, 1/1, 1/2, 1/4., 1/2t, 1/4, 1/8., 1/4t, 1/8, 1/16., 1/8t, 1/16, 1/32., 1/16t, 1/32, 1/64., 1/32t, 1/64 | |
| N:2946 | lfo1-1: Wave | 0-9 | Tri, Sqr, Sin, Saw, RevSaw, Exp, RevExp, Log, RevLog, S&H | |
| N:2947 | lfo1-1: Sync | 0-7 | None, NoteOn, NoteOff, Lfo1, Lfo2, Lfo3, Lfo4, Clock | |
| N:2948 | lfo1-1: Reset Phase | 0-16383 | | |
| | | | | |
| lfo1-2 | LFO 2 | | | #FF0088 |
| N:3072 | lfo1-2: Rate | 0-16383 | | |
| N:3073 | lfo1-2: Clock Mult | 0-19 | 8/1, 4/1, 2/1, 1/1, 1/2, 1/4., 1/2t, 1/4, 1/8., 1/4t, 1/8, 1/16., 1/8t, 1/16, 1/32., 1/16t, 1/32, 1/64., 1/32t, 1/64 | |
| N:3074 | lfo1-2: Wave | 0-9 | Tri, Sqr, Sin, Saw, RevSaw, Exp, RevExp, Log, RevLog, S&H | |
| N:3075 | lfo1-2: Sync | 0-7 | None, NoteOn, NoteOff, Lfo1, Lfo2, Lfo3, Lfo4, Clock | |
| N:3076 | lfo1-2: Reset Phase | 0-16383 | | |
| | | | | |
| lfo1-3 | LFO 3 | | | #00FF88 |
| N:3200 | lfo1-3: Rate | 0-16383 | | |
| N:3201 | lfo1-3: Clock Mult | 0-19 | 8/1, 4/1, 2/1, 1/1, 1/2, 1/4., 1/2t, 1/4, 1/8., 1/4t, 1/8, 1/16., 1/8t, 1/16, 1/32., 1/16t, 1/32, 1/64., 1/32t, 1/64 | |
| N:3202 | lfo1-3: Wave | 0-9 | Tri, Sqr, Sin, Saw, RevSaw, Exp, RevExp, Log, RevLog, S&H | |
| N:3203 | lfo1-3: Sync | 0-7 | None, NoteOn, NoteOff, Lfo1, Lfo2, Lfo3, Lfo4, Clock | |
| N:3204 | lfo1-3: Reset Phase | 0-16383 | | |
| | | | | |
| lfo1-4 | LFO 4 | | | #AA00FF |
| N:3328 | lfo1-4: Rate | 0-16383 | | |
| N:3329 | lfo1-4: Clock Mult | 0-19 | 8/1, 4/1, 2/1, 1/1, 1/2, 1/4., 1/2t, 1/4, 1/8., 1/4t, 1/8, 1/16., 1/8t, 1/16, 1/32., 1/16t, 1/32, 1/64., 1/32t, 1/64 | |
| N:3330 | lfo1-4: Wave | 0-9 | Tri, Sqr, Sin, Saw, RevSaw, Exp, RevExp, Log, RevLog, S&H | |
| N:3331 | lfo1-4: Sync | 0-7 | None, NoteOn, NoteOff, Lfo1, Lfo2, Lfo3, Lfo4, Clock | |
| N:3332 | lfo1-4: Reset Phase | 0-16383 | | |


## Part <device>: Performance

device: Redshift 6 Part <device>

| Control (Dec) | Label | Range | Choices | Color |
|---------------|-------|-------|---------|-------|
| perform1 | PERFORMANCE | | | #8800FF |
| N:512 | perform1: Pitch | 0-16383 | | |
| wheel1 | PITCH BEND | | | #FF8800 |
| N:1792 | wheel1: Bend Up | 0-24 | | |
| seq | SEQUENCER | | | #00FFDD |
| N:3456 | seq: Enabled | 0-1 | Off, On | |
| arp | ARPEGGIATOR | | | #FF0088 |
| N:3584 | arp: Clock Mult | 0-19 | 8/1, 4/1, 2/1, 1/1, 1/2, 1/4., 1/2t, 1/4, 1/8., 1/4t, 1/8, 1/16., 1/8t, 1/16, 1/32., 1/16t, 1/32, 1/64., 1/32t, 1/64 | |
| | | | | |
| | | | | |
| N:513 | perform1: Glide | 0-16383 | | |
| N:1793 | wheel1: Bend Down | 0-24 | | |
| N:3457 | seq: Engine | 0-0 | ClassicArp | |
| N:3585 | arp: Gate | 0-16383 | | |
| | | | | |
| | | | | |
| N:514 | perform1: Glide Mode | 0-1 | Normal, Legato | |
| | | | | |
| | | | | |
| N:3586 | arp: Mode | 0-5 | Up, Down, UpDown, UpDown2, Played, Random | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| N:3587 | arp: Octaves | 1-4 | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| N:3588 | arp: Sync | 0-1 | Off, On | |
| | | | | |
| | | | | |


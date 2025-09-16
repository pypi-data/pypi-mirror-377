# IDMTheory

IDMTheory is a python module with functions and data to support building of music theory applications.

## The Current State of IDMTheory

IDMTheory is currently in beta version.

## What's IDMTheory?

### Notes and Intervals

In IDMTheory, notes are represented by an integer type. Note value 0 corresponds to the C note in the first octave. Each positive integer step from 0 represents a semitone step in the chromatic scale.

Note names can use the note name style 'flat' or 'sharp'. Flat notation uses the 'b' character to indicate a flattened note (e.g. 'Gb') while sharp notation uses the '#' character to indicate a shapened note (e.g. 'F#').

![IDMTheory note values](https://i.imgur.com/XYJuJgU.png)

The following note intervals are defined:

- IDToneInterval.TONIC          =  0
- IDToneInterval.SEMI_TONE      =  1
- IDToneInterval.TONE           =  2 * SEMI_TONE
- IDToneInterval.MINOR_2ND      =  1 * SEMI_TONE
- IDToneInterval.MAJOR_2ND      =  2 * SEMI_TONE
- IDToneInterval.MINOR_3RD      =  3 * SEMI_TONE
- IDToneInterval.MAJOR_3RD      =  4 * SEMI_TONE
- IDToneInterval.PERFECT_4TH    =  5 * SEMI_TONE
- IDToneInterval.DIMINISHED_5TH =  6 * SEMI_TONE
- IDToneInterval.AUGMENTED_4TH  =  6 * SEMI_TONE
- IDToneInterval.TRITONE        =  6 * SEMI_TONE
- IDToneInterval.PERFERCT_5TH   =  7 * SEMI_TONE
- IDToneInterval.AUGMENTED_5TH  =  8 * SEMI_TONE
- IDToneInterval.MINOR_6TH      =  8 * SEMI_TONE
- IDToneInterval.MAJOR_6TH      =  9 * SEMI_TONE
- IDToneInterval.MINOR_7TH      = 10 * SEMI_TONE
- IDToneInterval.MAJOR_7TH      = 11 * SEMI_TONE
- IDToneInterval.PERFECT_OCTAVE = 12 * SEMI_TONE
- IDToneInterval.MINOR_9TH      = 13 * SEMI_TONE
- IDToneInterval.MAJOR_9TH      = 14 * SEMI_TONE
- IDToneInterval.PERFECT_11TH   = 17 * SEMI_TONE
- IDToneInterval.MAJOR_13TH     = 21 * SEMI_TONE
- IDToneInterval.OCTAVE         = PERFECT_OCTAVE

A set of functions and range transforms can be used to manipulate notes, for example:

- tone_interval_short_name
- normalize_tone_intervals
- transpose_tone_intervals

### Chords

The class IDChord represents a chord. A chord is defined by:

- Its tonic note.
- Its IDChordType: MAJOR, MINOR, DIMINISHED or AUGMENTED.
- A set of chord modifiers (aka flags), for example 'Dominant 7' or 'Major 7'.

The following chord modifiers are available:

- IDChordFlags.DOMINANT_7
- IDChordFlags.MAJOR_7
- IDChordFlags.DOMINANT_9
- IDChordFlags.DOMINANT_11  
- IDChordFlags.DOMINANT_13  
- IDChordFlags.ADD_2
- IDChordFlags.ADD_6
- IDChordFlags.ADD_9
- IDChordFlags.FLAT_5TH
- IDChordFlags.SUSPENDED_2ND
- IDChordFlags.SUSPENDED_4TH

Chord modifiers can be combined, e.g. IDChordFlags.DOMINANT_7 | IDChordFlags.ADD_9 gives a 7+9 chord.

The class IDChordDatabase can be used to create a database with thousands of different chords. The database can be used to find which chord(s) a certain intervals of notes represent, or chords that a similar to each other.

### Scales

The class IDScale can be used to define a specific note scale. Available scales are:

- Diatonic scales:
  - Natural Major
  - Dorian
  - Phrygian
  - Lydian
  - Mixolydian
  - Natural Minor
  - Locrian
- Harmonic scales:
  - Harmonic Minor
  - Locrian Natural 6
  - Major Augmented
  - Ukrainian Dorian
  - Phrygian Dominant
  - Lydian Natural 2
  - Super Locrian bb7
- Melodic scales:
  - Melodic Minor
  - Dorian b6
  - Lydian Augmented
  - Lydian Dominant
  - Mixolydian b6
  - Locrian #2
  - Super Locrian
  
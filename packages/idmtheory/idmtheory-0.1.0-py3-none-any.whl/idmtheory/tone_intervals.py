"""
This module defines basic tone intervals and some functions which can operate on them.
"""

__author__ = "https://codeberg.org/decoherence"

import itertools

class IDToneInterval:
    """Defines names and values for tone intervals."""
    # Interval definitions
    ROOT           =  0
    TONIC          =  0
    SEMI_TONE      =  1
    TONE           =  2 * SEMI_TONE
    MINOR_2ND      =  1 * SEMI_TONE
    MAJOR_2ND      =  2 * SEMI_TONE
    MINOR_3RD      =  3 * SEMI_TONE
    MAJOR_3RD      =  4 * SEMI_TONE
    PERFECT_4TH    =  5 * SEMI_TONE
    DIMINISHED_5TH =  6 * SEMI_TONE
    AUGMENTED_4TH  =  6 * SEMI_TONE
    TRITONE        =  6 * SEMI_TONE
    PERFECT_5TH    =  7 * SEMI_TONE
    AUGMENTED_5TH  =  8 * SEMI_TONE
    MINOR_6TH      =  8 * SEMI_TONE
    MAJOR_6TH      =  9 * SEMI_TONE
    MINOR_7TH      = 10 * SEMI_TONE
    MAJOR_7TH      = 11 * SEMI_TONE
    PERFECT_OCTAVE = 12 * SEMI_TONE
    MINOR_9TH      = 13 * SEMI_TONE
    MAJOR_9TH      = 14 * SEMI_TONE
    PERFECT_11TH   = 17 * SEMI_TONE
    MAJOR_13TH     = 21 * SEMI_TONE
    OCTAVE         = PERFECT_OCTAVE

    # Abbreviations
    P1 = TONIC
    R  = ROOT
    m2 = MINOR_2ND
    M2 = MAJOR_2ND
    m3 = MINOR_3RD
    M3 = MAJOR_3RD
    P4 = PERFECT_4TH
    dim5 = DIMINISHED_5TH
    Aug4 = AUGMENTED_4TH
    T = TRITONE    
    P5 = PERFECT_5TH    
    Aug5 = AUGMENTED_5TH
    m6 = MINOR_6TH    
    M6 = MAJOR_6TH
    m7 = MINOR_7TH
    M7 = MAJOR_7TH
    P8 = PERFECT_OCTAVE
    m9 = MINOR_9TH
    M9 = MAJOR_9TH
    P11 = PERFECT_11TH
    M13 = MAJOR_13TH
    O = OCTAVE

_TONE_INTERVALS_LONG_NAMES = {
    IDToneInterval.R:    "Root", 
    IDToneInterval.m2:   "minor 2nd",
    IDToneInterval.M2:   "Major 2nd",
    IDToneInterval.m3:   "minor 3rd",
    IDToneInterval.M3:   "Major 3rd",
    IDToneInterval.P4:   "Perfect 4th",
    IDToneInterval.dim5: "Tritone",
    IDToneInterval.P5:   "Perfect 5th",
    IDToneInterval.m6:   "minor 6th",
    IDToneInterval.M6:   "Major 6th",
    IDToneInterval.m7:   "minor 7",
    IDToneInterval.M7:   "Major 7",
    IDToneInterval.O:    "Octave",
    IDToneInterval.m9:   "minor 9th",
    IDToneInterval.M9:   "Major 9th",
    IDToneInterval.P11:  "Perfect 11th",
    IDToneInterval.M13:  "Major 13th"
    }

_TONE_INTERVALS_SHORT_NAMES = {
    IDToneInterval.R:    "R", 
    IDToneInterval.m2:   "m2",
    IDToneInterval.M2:   "M2",
    IDToneInterval.m3:   "m3",
    IDToneInterval.M3:   "M3",
    IDToneInterval.P4:   "P4",
    IDToneInterval.dim5: "dim5",
    IDToneInterval.P5:   "P5",
    IDToneInterval.m6:   "m6",
    IDToneInterval.M6:   "M6",
    IDToneInterval.m7:   "m7",
    IDToneInterval.M7:   "M7",
    IDToneInterval.O:    "O",
    IDToneInterval.m9:   "m9",
    IDToneInterval.M9:   "M9",
    IDToneInterval.P11:  "P11",
    IDToneInterval.M13:  "M13"
    }


def tone_interval_long_name(interval: int):
    return _TONE_INTERVALS_LONG_NAMES[interval]

def tone_interval_short_name(interval: int):
    return _TONE_INTERVALS_SHORT_NAMES[interval]


def normalize_tone_intervals(intervals: list[int] | set[int]) -> list[int]:
    """Normalizes a list of tone intervals to be in the range ROOT (0) to MAJOR_7TH (11)."""
    normalized_set = {v % IDToneInterval.OCTAVE for v in intervals}
    return sorted(normalized_set)


def transpose_tone_intervals(intervals: list[int], semi_tones: int) -> list[int]:
    """Transposes the given tone intervals a number of semi tone steps"""
    return [value + semi_tones for value in intervals if (value + semi_tones) >= 0]


def tone_intervals_signature(intervals: list[int]) -> int:
    """Translates a list of tone intervals to an interger number which is unique for the set of normalized intervals.

    Each bit in the signature represents a note in the normalized (see normalizeIntervals) interval:
        0: note not present
        1: note present
    
    Returns:
        A normalzed intervals signature number between 0 and 4095 (2^12 - 1).
    """
    signature = 0
    mask = 1
    
    for value in normalize_tone_intervals(intervals):
        signature = signature | (mask << value)
        
    return signature


def near_tone_intervals_signatures(signature: int, distance: int) -> list[int]:
    """Finds normalized intervals signatures which are close to a given signature
    
    Args:
        signature: The target signature (see toneIntervalsSignature).
        distance: The function will return signatures which are at this distance from the target signature.
          The distance is defined as number of notes which differs from the target signature.
    
    """
    near_signatures = []

    if distance < 0:
        raise ValueError("Distance must be positive or zero!")

    if distance == 0:
        return [signature]
    
    bits_to_toggle = [list(t) for t in itertools.combinations(range(IDToneInterval.OCTAVE), distance)]

    for bits in bits_to_toggle:
        mask = 0
        for bit in bits:                
            mask = mask | (1 << bit)

        near_signatures.append(signature ^ mask) # xor toggles the bits in the mask

    return near_signatures



"""
This module defines chords and functions for handling chords.
"""

__author__ = "https://codeberg.org/decoherence"

import copy
from itertools import combinations
from functools import reduce

from idroman import integer_to_roman

from .characters import IDMusicalChar
from .notes import note_name, note_to_note_value, generated_note_values
from .tone_intervals import IDToneInterval, tone_intervals_signature, near_tone_intervals_signatures


class IDScaleDegree:
    TONIC = 0
    SUPERTONIC = 1
    MEDIANT = 2
    SUBDOMINANT = 3
    DOMINANT = 4
    SUBMEDIANT = 5
    SUBTONIC = 6


SCALE_DEGREE_NAMES = {
    IDScaleDegree.TONIC: "Tonic", 
    IDScaleDegree.SUPERTONIC: "Supertonic", 
    IDScaleDegree.MEDIANT: "Mediant", 
    IDScaleDegree.SUBDOMINANT: "Subdominant", 
    IDScaleDegree.DOMINANT: "Dominant", 
    IDScaleDegree.SUBMEDIANT: "Submediant", 
    IDScaleDegree.SUBTONIC: "Subtonic"
    }
"""Mapping between relative note position in a scale and the name of the scale degree name."""


class _IDChordMod:
    """An IDChordModifier can be applied to a IDChord to alter its notes, e.g. to change a G chord to a G7 chord."""

    def __init__(self, long_name: str, short_name: str, to_add: list[int], to_remove: list[int], cancels: list[int]) -> None:
        """
        Args:
            long_name: The long name of the modifier, e.g. 'dominant 7'.
            short_name: The short name of the modifier, e.g. '7'.
            to_add: A list of relative intervals to be added to the chord, e.g. '[IDToneInterval.m7]'.
            to_remove: A list of relative intervals to be removed from the chord.
            cancels: A list of relative intervals which represents a modifier which shall be cancelled by this modifier.            
        """

        self._long_name = long_name
        self._short_name = short_name
        self._to_add = to_add
        self._to_remove = to_remove
        self._cancels = cancels

    
    def apply(self, tonic: int, intervals: list[int]) -> list[int]:
        """Applies this modifier to given input intervals and returns the result.
        
        All 'to_add' intervals are added and all 'to_remove' are removed from given 'intervals'.

        Args:
            tonic_note_value: The root note value to be used with 'source'.
            intervals: The input interval values
        """
        removing = [tonic + i for i in self._to_remove]
        adding   = [tonic + i for i in self._to_add]

        result = [v for v in intervals if v not in removing]
        result.extend(adding)
        result.sort()

        return result
    

    def append_short_name(self, input: str) -> str:
        """Returns the input string with the short name of the modifier appended."""
        return input + self._short_name
    

    def append_long_name(self, input: str) -> str:
        """Returns the input string with the long name of the modifier appended."""

        # Fix to avoid getting 'major major 7'
        if (" major" in input) and ("major 7" not in input):
            input = input.replace(" major", "")

        return input + " " + self._long_name
    

    def cancels_modifiers(self) -> list[int]:
        """Returns a list with the modifiers which shall be cancelled by this modifier."""
        return self._cancels
    

    def long_name(self) -> str:
        """Returns the long name of the modifier, e.g. 'dominant 7'."""
        return self._long_name
    

    def short_name(self) -> str:
        """Returns the short name of the modifier, e.g. '7'."""
        return self._short_name


    def __str__(self) -> str:
        """Enables print of IDChordModifier."""
        return f"IDChordMod({self._short_name})"
    

    def __repr__(self) -> str:        
        """Enables print of IDChordModifier."""
        return self.__str__()

    
class IDChordFlags:
    """Flags which identifies different chord modifiers; can be added toghether with the binary | operator."""
    NO_FLAG       = 0b0000000000000000
    DOMINANT_7    = 0b0000000000000001
    MAJOR_7       = 0b0000000000000010
    DOMINANT_9    = 0b0000000000000100
    DOMINANT_11   = 0b0000000000001000
    DOMINANT_13   = 0b0000000000010000
    ADD_2         = 0b0000000000100000
    ADD_6         = 0b0000000001000000
    ADD_9         = 0b0000000010000000
    FLAT_5TH      = 0b0000000100000000
    SUSPENDED_2ND = 0b0000001000000000
    SUSPENDED_4TH = 0b0000010000000000


CHORD_MODIFIERS = {
    IDChordFlags.DOMINANT_7:    _IDChordMod("dominant 7",    "7",    
                                            to_add=[IDToneInterval.m7], 
                                            to_remove=[],
                                            cancels=[]),

    IDChordFlags.MAJOR_7:       _IDChordMod("major 7",       "maj7", 
                                            to_add=[IDToneInterval.M7], 
                                            to_remove=[],
                                            cancels=[]),

    IDChordFlags.DOMINANT_9:    _IDChordMod("dominant 9",    "9",    
                                            to_add=[IDToneInterval.m7, IDToneInterval.M9], 
                                            to_remove=[], 
                                            cancels=[IDChordFlags.DOMINANT_7]),

    IDChordFlags.DOMINANT_11:   _IDChordMod("dominant 11",   "11",   
                                            to_add=[IDToneInterval.m7, IDToneInterval.M9, IDToneInterval.P11], 
                                            to_remove=[], 
                                            cancels=[IDChordFlags.DOMINANT_7, IDChordFlags.DOMINANT_9]),

    IDChordFlags.DOMINANT_13:   _IDChordMod("dominant 13",   "13",   
                                            to_add=[IDToneInterval.m7, IDToneInterval.M9, IDToneInterval.P11, IDToneInterval.M13], 
                                            to_remove=[],
                                            cancels=[IDChordFlags.DOMINANT_7, IDChordFlags.DOMINANT_9, IDChordFlags.DOMINANT_11]),

    IDChordFlags.SUSPENDED_2ND: _IDChordMod("suspended 2nd", "sus2", 
                                            to_add=[IDToneInterval.M2], 
                                            to_remove=[IDToneInterval.m3, IDToneInterval.M3],
                                            cancels=[]),

    IDChordFlags.SUSPENDED_4TH: _IDChordMod("suspended 4th", "sus4", 
                                            to_add=[IDToneInterval.P4], 
                                            to_remove=[IDToneInterval.m3, IDToneInterval.M3],
                                            cancels=[]),

    IDChordFlags.ADD_2:         _IDChordMod("add 2",         "+2", 
                                            to_add=[IDToneInterval.M2], 
                                            to_remove=[],
                                            cancels=[]),

    IDChordFlags.ADD_6:         _IDChordMod("add 6",         "+6",    
                                            to_add=[IDToneInterval.M6], 
                                            to_remove=[],
                                            cancels=[]),

    IDChordFlags.ADD_9:         _IDChordMod("add 9",         "+9", 
                                            to_add=[IDToneInterval.M9], 
                                            to_remove=[],
                                            cancels=[]),

    IDChordFlags.FLAT_5TH:      _IDChordMod("flat 5th",     "b5",   
                                            to_add=[IDToneInterval.dim5], 
                                            to_remove=[IDToneInterval.P5],
                                            cancels=[]),

}
"""Defines dictionary dict[IDChordModFlag, IDChordModifier] with available chord modifiers."""


def list_of_chord_flags_to_chord_flags(flags: list[int]) -> int:
    """Converts from a list of IDChordFlags to a combination of IDChordFlags as a single number."""
    return reduce(lambda acc, f: acc | f, flags, IDChordFlags.NO_FLAG)


def chord_flags_to_list_of_chord_flags(flags: int) -> list[int]:
    """Converts from a combination of IDChordFlags to a list of IDChordFlags."""
    return [f for f in CHORD_MODIFIERS.keys() if (f & flags) ]


class IDChordTemplate:
    """A template for different triad chord types, e.g. major, minor etc."""

    def __init__(self, long_name: str, short_name: str, intervals: list[int]) -> None:
        """
        Args:
            long_name: The long name of the chord type, e.g. 'minor'.
            short_name: The short name of the chord type, e.g. 'm'.
            intervals: A list of relative interval values which defines the chord type.
        """
        self._long_name = long_name
        self._short_name = short_name
        self._intervals = intervals


    def intervals(self) -> list[int]:
        return self._intervals


    def note_values(self, tonic: int) -> list[int]:
        """Returns the note values of the chord.
        
        Args:
            root: The root note value of the chord.
        """
        return [n + tonic for n in self._intervals]
    

    def short_name(self, tonic:int, style="flat") -> str:
        """Returns the short name of the chord, e.g. 'Cm'."""

        return note_name(tonic, style, include_octave=False) + self._short_name
    

    def short_type_name(self) -> str:
        """Retirns the short name of the chord type, e.g. 'm' for minor"""
        return self._short_name


    def long_type_name(self) -> str:
        """Retirns the long name of the chord type, e.g. 'minor'"""
        return self._long_name


    def long_name(self, tonic: int, style="flat") -> str:
        """Returns the long name of the chord, e.g. 'C minor'."""

        if len(self._long_name) > 0:
            space = " "
        else:
            space = ""

        return note_name(tonic, style, include_octave=False) + space + self._long_name


class IDChordType:
    """Definition of values representing the different types of triad chords."""
    MAJOR      = 1
    MINOR      = 2
    DIMINISHED = 3
    AUGMENTED  = 4 


CHORD_TYPES = {
    IDChordType.MAJOR:      IDChordTemplate("major",      "",                 [IDToneInterval.R, IDToneInterval.M3, IDToneInterval.P5]),
    IDChordType.MINOR:      IDChordTemplate("minor",      "m",                [IDToneInterval.R, IDToneInterval.m3, IDToneInterval.P5]),
    IDChordType.DIMINISHED: IDChordTemplate("diminished", IDMusicalChar.DIM,  [IDToneInterval.R, IDToneInterval.m3, IDToneInterval.dim5]),
    IDChordType.AUGMENTED:  IDChordTemplate("augmented",  "+",                [IDToneInterval.R, IDToneInterval.M3, IDToneInterval.Aug5])}
"""Dictionary dict[IDChordType, IDChordTemplate] which defines templates for avaliable triad chord types."""


def chord_scale_degree_to_roman(chord_type: int, scale_degree: int) -> str:
    """Returns the roman number symbol for given IDChordType and IDScaleDegree."""
    roman_case = {IDChordType.MAJOR: "upper", 
                  IDChordType.MINOR: "lower", 
                  IDChordType.DIMINISHED: "lower", 
                  IDChordType.AUGMENTED: "lower"}
    
    post_fix = {IDChordType.MAJOR: "", 
                IDChordType.MINOR: "", 
                IDChordType.DIMINISHED: IDMusicalChar.DIM, 
                IDChordType.AUGMENTED: "+"}

    return integer_to_roman(scale_degree + 1, roman_case[chord_type]) + post_fix[chord_type]
    


class IDChord:
    """Represents a chord which can be modified by applying IDChordMods."""

    def __init__(self, tonic: int | str, type: int, flags: int | list[int] = IDChordFlags.NO_FLAG) -> None:
        """
        Args:
            tonic: Root note value OR root note name of the chord.
            type: The IDChordType which defines the type of the chord.
            flags (optional): A list of IDChordFlags which each represents a chord modifier to be applyed, OR
              an integer with accumulated IDChordFlags, e.g. 'IDChordFlags.DOMINANT_7 | IDChordFlags.ADD_9'.
        """
        self._tonic = note_to_note_value(tonic)
        self._type = type
        self._flags: list[int] = []    
        self._inversion = 0 
    
        self.set_flags(flags)


    def clone(self) -> 'IDChord':
        """Returns a deep copy of the chord."""

        return copy.copy(self)
    

    def cycle_inversion(self):
        """Increases the inversion by one, module number of notes of the chord."""
        self.set_inversion(self._inversion + 1)


    def flags(self) -> int:
        """Returns the current modifications of the chord as a combination of IDChordFlags."""
        return list_of_chord_flags_to_chord_flags(self._flags)


    def harmony(self) -> set[int]:
        """Returns the harmony of the chord as a set of note values.
        
        The tonic note will be in octave 0.
        Selected inversion will be applied (see set_inversion).
        """
        return set(self.note_values())


    def inversion(self) -> int:
        """Returns the current inversion (0-7) of the chord."""
        return self._inversion


    def long_name(self, style="flat") -> str:
        """Returns the full long name of the chord including modifiers."""
        name = self._template().long_name(self._tonic, style)

        for flag in self._flags:
            name = CHORD_MODIFIERS[flag].append_long_name(name)

        return name


    def note_values(self) -> list[int]:
        """Returns the note values of the chord.
        
        The tonic note will be in octave 0.
        Selected inversion will be applied (see set_inversion).
        """
        values = self._template().note_values(self._tonic)

        # apply modifiers
        for flag in self._flags:            
            values = CHORD_MODIFIERS[flag].apply(self._tonic, values)

        # apply inversion        
        for _ in range(self._inversion):
            values = [values[-1] - IDToneInterval.OCTAVE] + values[:-1]            
            if values[0] < 0:
                values = [i + IDToneInterval.OCTAVE for i in values]

        return values


    def number_of_flags(self) -> int:
        return len(self._flags)


    def number_of_notes(self) -> int:
        """Returns the number of notes of the chord."""
        return len(self.note_values())


    def set_flags(self, flags: int | list[int]):
        """Sets the modifications which shall be applied to the chord.
        
        Args:
            flags: A list of IDChordFlags which each represents a chord modifier to be applyed, OR
            an integer with accumulated IDChordFlags, e.g. 'IDChordFlags.DOMINANT_7 | IDChordFlags.ADD_9'.
        """
        temp_flags = []

        if (isinstance(flags, list)):
            temp_flags = [f for f in flags if f != IDChordFlags.NO_FLAG]

        if (isinstance(flags, int)):
            if (flags != IDChordFlags.NO_FLAG):        
                temp_flags = chord_flags_to_list_of_chord_flags(flags)

        flags_to_be_canceled = {f for g in temp_flags for f in CHORD_MODIFIERS[g].cancels_modifiers()}
        self._flags = [f for f in temp_flags if f not in flags_to_be_canceled]
        

    def set_inversion(self, steps: int):
        """Sets the inversion of the chord.

        When a chord is inverted, the root note will no longer be the lowest note of the chord.
        For each inversion step, another of the notes of the chord will be the lowest note
        of the chord.
        
        Args:
            steps: The number of inversion steps. Inversion steps are modulo N, where N is
              the number of notes of the chord, i.e. inversion N + 1 = inversion 0.            
        """
        self._inversion = steps % self.number_of_notes()


    def set_tonic(self, tonic: int | str):
        """Sets the root note of the chord.
        
        Args:
            root: Note value OR note name.
        """
        self._tonic = note_to_note_value(tonic)


    def set_type(self, type: int):
        """Sets the type of the chord.

        Args:
            type: The IDChordType which defines the type of the chord.
        """
        self._type = type


    def short_mod_name(self, style="flat") -> str:
        """Returns the combined short name of the modifiers and inversion, without the tonic note name and the chord type, e.g. '7add9/G'."""
        name = ""

        for flag in self._flags:
            name = CHORD_MODIFIERS[flag].append_short_name(name)

        base_note_value = self.note_values()[0]
        if base_note_value != self._tonic:
            name = name + "/" + note_name(base_note_value, style, include_octave=False)

        return name


    def short_name(self, style="flat") -> str:
        """Returns the full short name of the chord including modifiers and inversion."""
        return self.short_type_name(style) + self.short_mod_name()


    def short_type_name(self, style="flat") -> str:
        """Returns the short name of the chord without modifiers, i.e. 'C#m' for 'minor'."""
        return self._template().short_name(self._tonic, style)


    def signature(self) -> int:
        return tone_intervals_signature(self.note_values())


    def tonic_note_value(self) -> int:
        """Returns the root note value of the chord."""
        return self._tonic
    

    def type(self) -> int:
        """Returns the IDChordType of the chord."""
        return self._type


    def _template(self) -> IDChordTemplate:
        return CHORD_TYPES[self._type]
    

    def __eq__(self, other) -> bool:
        """Compare operator for IDChord.
        
        Args:
            other: IDChord.
        """

        if isinstance(other, IDChord):
            return self.note_values() == other.note_values()
        
        if isinstance(other, list):
            return self.note_values() == other
                
        raise ValueError("Invalid type!")
    

    def __hash__(self):
        return hash(tuple(self.note_values())) 
    

    def __ne__(self, other) -> bool:
        """Compare operator for IDChord."""
        return not self.__eq__(other)


    def __str__(self):
        """Enables print of IDChord."""
        return f"IDChord({self.long_name()} | {self.short_name()})"
    

    def __repr__(self):
        """Enables print of IDChord."""
        return self.__str__()
    

class IDChordDatabase:
    """An instance of this class is a database with chords of all types, all normalized root notes and 
    combinations of chord modifications.    
    """

    def __init__(self, number_mod_combinations = 3) -> None:
        """
        Args:
            number_mod_combinations (optional): An integer which defines the number of combinations of
              chord modifications will be applied when the database is created.
        """
        
        self._chord_database: dict[int, set[IDChord]] = dict()
        """The chord database is a directory with the chord signature as key value. Since different
        chords can have the same signature, each database entry may contain several chords.
        """

        print("Creating chord database ...")

        all_chord_flags = [IDChordFlags.NO_FLAG, *CHORD_MODIFIERS.keys()]
        chord_flag_combinations = [list(c) for c in combinations(all_chord_flags, number_mod_combinations)]
        
        for tonic in generated_note_values("C", IDToneInterval.OCTAVE):
            for type in CHORD_TYPES.keys():
                self._add_chord(IDChord(tonic, type, IDChordFlags.NO_FLAG))

                for flags in chord_flag_combinations:
                    self._add_chord(IDChord(tonic, type, flags))


        print(f"  Chords in database: {self.size()}")
        print(f"  Unique chord signatures in database: {len(self._chord_database)}")


    def _add_chord(self, chord: IDChord) -> None:
        signature = chord.signature()

        if (not signature in self._chord_database.keys()):
            self._chord_database[signature] = set()
        signature_entry = self._chord_database[signature]

        # remove chords with identical note values with more flags or more complex flags
        for existing_chord in signature_entry:
            if (chord == existing_chord):
                if (chord.number_of_flags() < existing_chord.number_of_flags()):
                    signature_entry.remove(existing_chord)
                    break
                elif (chord.flags() < existing_chord.flags()):                    
                    signature_entry.remove(existing_chord)
                    break

        signature_entry.add(chord)


    def size(self) -> int:
        """Returns the number of chords in the database."""
        result = 0

        for chords in self._chord_database.values():
            result += len(chords)

        return result
    

    def match(self, intervals: list[int], distance: int = 0) -> list[IDChord]:
        """Returns chords found in the database which matches the input intervals.
        
        Args:
            intervals: The input intervals are normalized and compared with the
              normalized intervals of the chords in the database.
            distance: The number of notes which shall differ to make a match, e.g.
              distance = 0 returns exact matches, distance = 1 returns chords which
              differs with one note.
        """
        chords: list[IDChord] = []
        input_signature = tone_intervals_signature(intervals)        
        signatures_to_seach_for = near_tone_intervals_signatures(input_signature, distance)        


        for signature in signatures_to_seach_for:
            if signature in self._chord_database:
                chords.extend(self._chord_database[signature])

        return chords


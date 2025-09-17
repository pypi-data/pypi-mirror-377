"""
Copyright (C) 2025 drd <drd.ltt000@gmail.com>

This file is part of TunEd.

TunEd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TunEd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np


# Dictionnaire des formules d'accords (intervalles en demi-tons depuis la fondamentale)
CHORD_FORMULAS = {
    # Accords a 3 sons
    "Maj": (0, 4, 7),      # F 3 5
    "min": (0, 3, 7),      # F 3m 5
    "sus4": (0, 5, 7),     # F 4 5
    "sus2": (0, 2, 7),     # F 2 5
    "dim": (0, 3, 6),      # F 3m b5
    "aug": (0, 4, 8),      # F 3 #5
    # Accords a 4 sons
    "7": (0, 4, 7, 10),    # F 3 5 7
    "Maj7": (0, 4, 7, 11), # F 3 5 Maj7
    "min7": (0, 3, 7, 10), # F 3m 5 7
}


def frequency_to_midi(frequency, ref_freq):
    """Converts a frequency in Hz to a MIDI note number."""
    if frequency == 0:
        return 0
    midi_note = int(round(69 + (12 * np.log2(frequency / ref_freq)) / np.log2(2)))
    return midi_note


def midi_to_frequency(midi_note, ref_freq):
    """Converts a MIDI note number to a frequency in Hz."""
    return ref_freq * 2.0 ** ((midi_note - 69) / 12.0)


def midi_to_ansi_note(midi_note):
    """Converts a MIDI note number to its name (e.g., 'A', 'C#') and octave."""
    if midi_note == 0:
        return "-", 0
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    num_notes = len(notes)
    note_name = notes[int((midi_note - 21) % num_notes)]
    note_number = (midi_note - 12) // num_notes
    return note_name, note_number

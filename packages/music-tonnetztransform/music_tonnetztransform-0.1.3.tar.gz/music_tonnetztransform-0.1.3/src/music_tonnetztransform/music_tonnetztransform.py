from itertools import permutations
from music21 import note, pitch
import random
import re

import sys
sys.path.append('./src')
from music_tonnetztransform.neo_riemann_tonnetz import Tonnetz
from music_melodicdevice import Device

class Transform:
    def __init__(
        self,
        base_note='C',
        base_octave=4,
        chord_quality='', # '': major, 'm': minor, '7': ...
        format='midinum', # or ISO for names
        semitones=7, # transposition semitones
        max=4, # number of circular transformations
        allowed=None, # [T], [N], [T,N], None
        transforms=4, # either a list or a number of computed transformations
        verbose=False,
    ):
        self.base_note = base_note
        self.base_octave = base_octave
        self.chord_quality = chord_quality
        self.format = format
        self.semitones = semitones
        self.max = max
        self.allowed = allowed if allowed is not None else ['T', 'N']
        self.transforms = transforms
        self.verbose = verbose
        self.nrt = Tonnetz()
        self.mdt = Device(scale_note=base_note, verbose=verbose)
        self.base_chord = self._build_base_chord()

    def _build_base_chord(self):
        if self.chord_quality == 'm':
            intervals = [0, 3, 7]
        elif self.chord_quality == '7':
            intervals = [0, 4, 7, 10]
        else:
            intervals = [0, 4, 7]
        base_midi = self._note_to_midi(self.base_note, self.base_octave)
        return [ base_midi + i for i in intervals ]

    def _note_to_midi(self, note, octave=None):
        if not octave:
            m = re.match(r'^([A-G][#b]?)(\d+)$', str(note))
            if m:
                note = m.group(1)
                octave = m.group(2)
        p = pitch.Pitch(str(note) + str(octave))
        return p.midi

    def _build_transform(self):
        if isinstance(self.transforms, list):
            return list(self.transforms)
        elif isinstance(self.transforms, int):
            transforms = ['O', 'I']
            if 'T' in self.allowed:
                transforms += [f"T{i}" for i in range(1, self.semitones + 1)]
                transforms += [f"T-{i}" for i in range(1, self.semitones + 1)]
            if 'N' in self.allowed:
                if self.chord_quality == '7':
                    transforms += [
                        'S23', 'S32', 'S34', 'S43', 'S56', 'S65',
                        'C32', 'C34', 'C65'
                    ]
                else:
                    alphabet = ['P', 'R', 'L']
                    transforms += alphabet
                    transforms += [ ''.join(p) for p in permutations(alphabet, 2) ]
                    transforms += [ ''.join(p) for p in permutations(alphabet, 3) ]
            return [ random.choice(transforms) for _ in range(self.transforms) ]
        else:
            raise ValueError("Invalid transforms")

    def _build_chord(self, token, pitches, notes):
        if token == 'O':
            chord = pitches
        elif token == 'I':
            chord = notes
        elif token.startswith('T'):
            semitones = int(token[1:])
            chord = self.mdt.transpose(semitones, [ self._pitchname(n) for n in notes ])
            chord = [ self._note_to_midi(c) for c in chord ]
        else:
            op = token
            if len(token) > 1 and not any(c.isdigit() for c in token):
                op = self.nrt.taskify_tokens(token)
            chord = self.nrt.transform(op, [ pitch.Pitch(n).midi for n in notes ])
        return chord

    def _pitchname(self, midi_num):
        n = note.Note()
        n.pitch.midi = midi_num
        name = n.nameWithOctave
        name = re.sub(r'\-', 'b', name)
        return name

    def _strip_octave(self, note):
        m = re.match(r'^([A-G][#b]?)(\d+)$', note)
        return m.group(1) if m else note

    def _rand_bool(self):
        return random.randint(0, 1) == 1

    def generate(self):
        pitches = notes = self.base_chord
        transforms = self._build_transform()
        chords = []
        generated = []
        for i, token in enumerate(transforms, 1):
            transformed = self._build_chord(token, pitches, notes)
            note_names = [ self._pitchname(n) for n in transformed ]
            chord = [ self._strip_octave(n) for n in note_names ]
            generated.append(note_names if self.format == 'ISO' else transformed)
            chords.append(chord)
            notes = transformed
        if self.verbose:
            print("Generate:", generated)
        return generated, transforms, chords

    def circular(self):
        pitches = notes = self.base_chord
        transforms = self._build_transform()
        chords = []
        generated = []
        posn = 0
        for i in range(1, self.max + 1):
            token = transforms[posn % len(transforms)]
            transformed = self._build_chord(token, pitches, notes)
            note_names = [ self._pitchname(n) for n in transformed ]
            chord = [ self._strip_octave(n) for n in note_names ]
            generated.append(note_names if self.format == 'ISO' else transformed)
            chords.append(chord)
            notes = transformed
            posn = posn + 1 if self._rand_bool() else posn - 1
        if self.verbose:
            print("Circular:", generated)
        return generated, transforms, chords

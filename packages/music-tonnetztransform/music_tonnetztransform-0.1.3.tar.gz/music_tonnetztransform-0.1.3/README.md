# Music Tonnetz-Transform
Perform Neo-Riemann operations on musical chords

## DESCRIPTION

This class generates transposed and Neo-Riemann chord progressions.

Calling the `generate()` and `circular()` methods returns three lists:

1. The generated chord progression (in either the default midi-number or named "ISO" format)
2. The transformations used in the generation
3. The list of pitch names, comprising the chords that were generated

The `generate()` method generates a *linear* series of transformed chords.

The `circular()` method generates a *circular* series of transformed chords. This describes movement around a circular list ("necklace") of chord transformations. Starting at position zero, we move randomly, forward or backward along the necklace, transforming the current chord.

## SYNOPSIS
```python
from music_tonnetztransform import Transform

t = Transform( # defaults:
    base_note='C',
    base_octave=4,
    chord_quality='', # '': major, 'm': minor, '7': 7th
    format='midinum', # or ISO for names
    semitones=7, # transposition semitones
    max=4, # number of circular transformations
    allowed=None, # [T], [N], [T,N], None
    transforms=4, # either a list or a number of computed transformations
    verbose=False,
)

generated, transforms, chords = t.generate()
# [[63, 67, 70], [70, 74, 77], [70, 75, 79], [70, 75, 79]],
# ['T3', 'T7', 'RL', 'I'],
# [['Eb', 'G', 'Bb'], ['Bb', 'D', 'F'], ['Bb', 'Eb', 'G'], ['Bb', 'Eb', 'G']])

t = Transform(format="ISO")
generated, transforms, chords = t.generate()
# [['G4', 'B4', 'D5'], ['D4', 'F#4', 'A4'], ['C#4', 'F4', 'G#4'], ['D4', 'F4', 'Bb4']],
# ... as above

t = Transform(format='ISO', transforms=['R','L','P'])
generated = t.generate()[0] # [['C4', 'E4', 'A4'], ['C4', 'F4', 'A4'], ['C4', 'F4', 'G#4']]

t = Transform(transforms=['R','L','P','T2'], max=6)
generated, transforms, chords = t.circular()
```

## MUSICAL EXAMPLES
```python
from music_tonnetztransform import Transform
from music21 import chord, stream

s = stream.Stream()
p = stream.Part()

t = Transform()
generated = t.generate()[0]

for notes in generated:
    c = chord.Chord(notes, type='whole')
    p.append(c)

s.append(p)
s.show()
```

```python
from music21 import duration, chord, stream
from music_tonnetztransform import Transform
from random_rhythms import Rhythm

s = stream.Stream()
p = stream.Part()

r = Rhythm(durations=[1, 3/2, 2])
motif = r.motif()

t = Transform(max=len(motif))
generated = t.circular()[0]

for i,dura in enumerate(motif):
    c = chord.Chord(generated[i])
    c.duration = duration.Duration(dura)
    p.append(c)

s.append(p)
s.show()
```

```python
from music21 import duration, chord, stream
from chord_progression_network import Generator
from music_tonnetztransform import Transform
from random_rhythms import Rhythm

s = stream.Stream()
p = stream.Part()

r = Rhythm(durations=[1, 3/2, 2])
motifs = [ r.motif() for _ in range(3) ]

t = Transform(max=len(motifs[0]))
generated = t.circular()[0]

g = Generator()

for motif in motifs:
    g.max = len(motif)
    phrase = g.generate()
    for i,dura in enumerate(motif):
        c = chord.Chord(phrase[i])
        c.duration = duration.Duration(dura)
        p.append(c)

for i,dura in enumerate(motifs[0]):
    c = chord.Chord(generated[i])
    c.duration = duration.Duration(dura)
    p.append(c)

s.append(p)
s.show()
```

## SEE ALSO

https://metacpan.org/pod/Music::NeoRiemannianTonnetz

https://en.wikipedia.org/wiki/Neo-Riemannian_theory

https://viva.pressbooks.pub/openmusictheory/chapter/neo-riemannian-triadic-progressions/

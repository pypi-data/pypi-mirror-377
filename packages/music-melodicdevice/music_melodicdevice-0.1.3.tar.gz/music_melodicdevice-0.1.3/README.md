# Music Melodic-Device
Apply chromatic and diatonic transformations to music notes

## DESCRIPTION

This class provides methods to do chromatic and diatonic transformations to music notes.

The three major categories are transpositions, inversions, and five types of ornamentation.

## SYNOPSIS
```python
from music_melodicdevice import Device

# default scale: chromatic
device = Device(notes=['C4', 'E4', 'D4', 'G4', 'C5'])
notes = device.transpose(2) # ['D4', 'F#4', 'E4', 'A4', 'D5']
notes = device.invert('C4') # ['C4', 'G#3', 'A#3', 'F3', 'C3']

# diatonic transformation:
device = Device(scale_name='major', verbose=True)
device.notes = ['C4', 'E4', 'D4', 'G4', 'C5']
notes = device.transpose(2) # ['E4', 'G4', 'F4', 'B4', 'E5']
notes = device.invert('C4') # ['C4', 'A3', 'B3', 'F3', 'C3']

# unknown note:
device = Device()
device.build_scale('major')
notes = device.transpose(2, ['C4', 'E4', 'D#4', 'G4', 'C5'])
# ['E4', 'G4', None, 'B4', 'E5']
notes = device.invert('C4', ['C4', 'E4', 'D#4', 'G4', 'C5'])
# ['C4', 'A3', None, 'F3', 'C3']

# Ornamentation:

# chromatic
device = Device()

notes = device.grace_note(1, 'D5') # [[1/16, 'D5'], [1 - 1/16, 'D5']])
notes = device.grace_note(1, 'D5', offset=1) # [[1/16, 'D#5'], [1 - 1/16, 'D5']])
notes = device.grace_note(1, 'D5', offset=-1) # [[1/16, 'C#5'], [1 - 1/16, 'D5']])

notes = device.turn(1, 'D5') # [[1/4,'D#5'], [1/4,'D5'], [1/4,'C#5'], [1/4,'D5']])
notes = device.turn(1, 'D5', offset=-1) # [[1/4,'C#5'], [1/4,'D5'], [1/4,'D#5'], [1/4,'D5']])

notes = device.trill(1, 'D5', number=2, offset=1)
# [[1/4,'D5'], [1/4,'D#5'], [1/4,'D5'], [1/4,'D#5']])
notes = device.trill(1, 'D5', number=2, offset=-1)
# [[1/4,'D5'], [1/4,'C#5'], [1/4,'D5'], [1/4,'C#5']])

notes = device.mordent(1, 'D5', offset=1) # [[1/4,'D5'], [1/4,'D#5'], [1/2,'D5']])
notes = device.mordent(1, 'D5', offset=-1) # [[1/4,'D5'], [1/4,'C#5'], [1/2,'D5']])

notes = device.slide(1, 'D5', 'F5') # [[1/4,'D5'], [1/4,'D#5'], [1/4,'E5'], [1/4,'F5']])
notes = device.slide(1, 'D5', 'B4') # [[1/4,'D5'], [1/4,'C#5'], [1/4,'C5'], [1/4,'B4']])

# diatonic
device = Device(scale_name='major')

notes = device.grace_note(1, 'D5') # [[1/16, 'D5'], [1 - 1/16, 'D5']])
notes = device.grace_note(1, 'D5', offset=1) # [[1/16, 'E5'], [1 - 1/16, 'D5']])
notes = device.grace_note(1, 'D5', offset=-1) # [[1/16, 'C5'], [1 - 1/16, 'D5']])

notes = device.turn(1, 'D5', offset=1) # [[1/4,'E5'], [1/4,'D5'], [1/4,'C5'], [1/4,'D5']])
notes = device.turn(1, 'D5', offset=-1) # [[1/4,'C5'], [1/4,'D5'], [1/4,'E5'], [1/4,'D5']])

notes = device.trill(1, 'D5', number=2, offset=1) # [[1/4,'D5'], [1/4,'E5'], [1/4,'D5'], [1/4,'E5']])
notes = device.trill(1, 'D5', number=2, offset=-1) # [[1/4,'D5'], [1/4,'C5'], [1/4,'D5'], [1/4,'C5']])

notes = device.mordent(1, 'D5', offset=1) # [[1/4,'D5'], [1/4,'E5'], [1/2,'D5']])
notes = device.mordent(1, 'D5', offset=-1) # [[1/4,'D5'], [1/4,'C5'], [1/2,'D5']])
```

## METHODS

### transpose
```python
notes = device.transpose(amount)
```

Transpose a note by an integer amount.

### invert
```python
notes = device.invert(axis_note, note_list)
```

Invert the `note_list` of named notes, around the named `axis_note`.

### grace_note
```python
notes = device.grace_note(duration, pitch, offset=offset)
```

Return a list with a 64th-note grace-note and the original named `pitch` with octave. The grace-note is `offset` semi-tone steps from the given `pitch`. The `duration` is the total, original length of the `pitch`.

### turn
```python
notes = device.turn(duration, pitch, offset=offset)
```

Return a list of four notes, having an up-down pattern, in place of the given `pitch` and `duration`.

### trill
```python
notes = device.trill(duration, pitch, number=number, offset=offset)
```

Return a list of pairs of notes, given the `number`, in place of the given `pitch` and `duration`.

The first of the pair is part of the original note, and the second is the note plus the given `offset`.

### mordent
```python
notes = device.mordent(duration, pitch, offset=offset)
```

Return a list of three notes in place of the given `pitch` and `duration`.

### slide
```python
notes = device.slide(duration, from_pitch, to_pitch)
```

Return a list of chromatic notes inclusively between the `from_pitch` and `to_pitch`, in place of the given `duration`.

## MUSICAL EXAMPLES
```python
from music21 import duration, note, stream
from music_melodicdevice import Device

device = Device(notes=['C4', 'E4', 'D4', 'G4'])
notes = device.invert('C5')

s = stream.Stream()
p = stream.Part()

for i in device.notes + notes:
    n = note.Note(i)
    n.duration = duration.Duration(1)
    p.append(n)

s.append(p)
s.show()
```
```python
notes = ['C4', 'E4', 'D4', 'G4']

device = Device(scale_name='major')
device.notes = notes
device.notes = device.invert('C5')
device.notes = device.transpose(-5)

s = stream.Stream()
p = stream.Part()

for i,j in enumerate(notes + device.notes):
    if (i + 1) % 4 == 0:
        turn = device.turn(1, j)
        for t in turn:
            m = note.Note(t[1])
            m.duration = duration.Duration(t[0])
            p.append(m)
    else:
        n = note.Note(j)
        n.duration = duration.Duration(1)
        p.append(n)

s.append(p)
s.show()
```

# SEE ALSO

https://en.wikipedia.org/wiki/Inversion_(music)#Melodies

https://en.wikipedia.org/wiki/Ornament_(music)

import sys
sys.path.append('./src')
import music_melodicdevice.musical_scales as musical_scales
from music21 import pitch, note
import re

class Device:
    def __init__(self, scale_note='C', scale_name='chromatic', notes=[], flat=False, verbose=0):
        self.scale_note = scale_note
        self.scale_name = scale_name
        self.notes = notes
        self.flat = flat
        self.verbose = verbose
        self.scale = self.build_scale()

    def _find_pitch(self, p):
        m = re.search(r'^.b\d$', p)
        if m:
            p = re.sub(r'b', '-', p)
        try:
            i = self.scale.index(p)
        except ValueError:
            try:
                n = pitch.Pitch(p).getEnharmonic()
                i = self.scale.index(n.nameWithOctave)
            except ValueError:
                i = -1
        return i

    def build_scale(self, name=None):
        if name:
            self.scale_name = name
        scale = []
        for i in range(-1,10):
            s = musical_scales.scale(self.scale_note, self.scale_name, starting_octave=i)
            scale.append(s[:-1])
        scale = [ f"{x}" for y in scale for x in y ]
        if self.flat:
            top = scale[:12]
            bottom = scale[13:]
            temp = []
            for n in bottom:
                m = note.Note(n)
                if m.pitch.accidental:
                    p = pitch.Pitch(m.nameWithOctave).getEnharmonic()
                    temp.append(p.nameWithOctave)
                else:
                    temp.append(m.nameWithOctave)
            scale = top + temp
        if self.verbose:
            print("Scale:", scale, len(scale))
        return scale

    def transpose(self, offset, notes=[]):
        if not notes:
            notes = self.notes
        if self.verbose:
            print("Notes:", notes)
        transposed = []
        for n in notes:
            i = self._find_pitch(n)
            if i == -1:
                transposed.append(None)
            else:
                val = self.scale[i + offset]
                transposed.append(val)
        if self.verbose:
            print('Transposed:', transposed)
        return transposed

    def intervals(self, notes=[]):
        if not notes:
            notes = self.notes
        pitches = []
        for note in notes:
            i = self._find_pitch(note)
            pitches.append(i)
        if self.verbose:
            print(f"Pitch indexes: {pitches}")
        intervals = []
        last = None
        for pitch in pitches:
            if last is not None:
                intervals.append(pitch - last)
            last = pitch
        if self.verbose:
            print(f"Intervals: {intervals}")
        return intervals

    def invert(self, axis_note, notes=[]):
        if not notes:
            notes = self.notes
        if self.verbose:
            print("Axis, Notes:", axis_note, notes)
        axis = self._find_pitch(axis_note)
        nums = [ self._find_pitch(n) for n in notes ]
        inverted = []
        for n in nums:
            if n == -1:
                inv = None
            else:
                inv = axis - (n - axis)
            inverted.append(inv)
        named = []
        for x in inverted:
            if not x:
                name = None
            else:
                name = self.scale[x]
            named.append(name)
        if self.verbose:
            print("Inverted:", named)
        return named

    def grace_note(self, duration, pitch, offset=0):
        i = self._find_pitch(pitch)
        grace_note = self.scale[i + offset]
        x = duration
        y = 1/16 # 64th note
        z = x - y
        if self.verbose:
            print(f"Durations: {x} + {y} = {z}")
        return [[y, grace_note], [z, pitch]]

    def turn(self, duration, pitch, offset=1):
        factor = 4
        i = self._find_pitch(pitch)
        above = self.scale[i + offset]
        below = self.scale[i - offset]
        x = duration
        z = x / factor
        if self.verbose:
            print(f"Durations: {x}, {z}")
        return [[z, above], [z, pitch], [z, below], [z, pitch]]

    def trill(self, duration, pitch, number=2, offset=1):
        i = self._find_pitch(pitch)
        alt = self.scale[i + offset]
        x = duration
        z = x / number / 2
        if self.verbose:
            print(f"Durations: {x}, {z}")
        trill = []
        for _ in range(number):
            trill.append([z, pitch])
            trill.append([z, alt])
        return trill

    def mordent(self, duration, pitch, offset=1):
        factor = 4
        i = self._find_pitch(pitch)
        alt = self.scale[i + offset]
        x = duration
        y = x / factor
        z = x - (2 * y)
        if self.verbose:
            print(f"Durations: {x}, {y}, {z}")
        return [[y, pitch], [y, alt], [z, pitch]]

    def slide(self, duration, from_pitch, to_pitch):
        # Always use the chromatic scale for slide
        scale_name = self.scale_name
        self.scale = self.build_scale('chromatic')
        i = self._find_pitch(from_pitch)
        j = self._find_pitch(to_pitch)
        start, end = (i, j) if i <= j else (j, i)
        x = duration
        y = end - start + 1
        z = x / y
        if self.verbose:
            print(f"Durations: {x}, {y}, {z}")
        notes = []
        for idx in range(start, end + 1):
            n = self.scale[idx]
            notes.append([z, n])
        if j < i:
            notes = list(reversed(notes))
        self.scale = self.build_scale(scale_name)
        return notes

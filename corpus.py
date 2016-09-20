from music21 import converter, clef, stream, pitch, note, meter, midi
import numpy as np


KEY_SIG_OFFSET = 0

def parse_notes(midi_stream):
    melody_corpus = []

    last_pitch = 1
    chord_buffer = []
    prev_offset = 0.0
    for m in midi_stream.measures(1, None):
        time_sig = m.timeSignature
        for nr in m.flat.notesAndRests:
            offset_loc = nr.offset
            # pitch = nr.pitch.pitchClass + 1  if isinstance(nr, note.Note) else 0
            pitch = nr.pitch.midi  if isinstance(nr, note.Note) else 0
            beat_strength = round(nr.beatStrength * 4.0, 0)
            duration = float(nr.quarterLength)

            note_repr = (pitch, beat_strength, duration)
            # note_repr = (pitch, duration)
            # Handle chords
            if nr.offset == prev_offset:
                if note_repr[0] > 0:
                    chord_buffer.append(note_repr)
            else:
                if chord_buffer: # Choose tone from chord buffer closest to current note
                    chord_melody_tone = sorted(chord_buffer, key=lambda x: abs(x[0] - pitch))[0]
                    melody_corpus.append(chord_melody_tone)
                melody_corpus.append(note_repr)
                chord_buffer = []
            prev_offset = nr.offset

    return melody_corpus


def build_corpus(midi_files):
    melody_corpus = []
    for file in midi_files:
        midi_stream = converter.parse(file)
        midi_stream = midi_stream[0]
        if '1008' in file or '1011' in file:
            midi_stream.keySignature = midi_stream.keySignature.relative
        key_sig = midi_stream.keySignature
        print('Input file: {} ({})'.format(file, str(key_sig)))
        midi_stream.transpose(KEY_SIG_OFFSET - key_sig.tonic.pitchClass, inPlace=True)
        melody_corpus.extend(parse_notes(midi_stream))
    # map indices for constructing matrix representations
    melody_set = set(melody_corpus)
    notes_indices = {note: i for i, note in enumerate(melody_set)}
    indices_notes = {i: note for i, note in enumerate(melody_set)}

    return melody_corpus, melody_set, notes_indices, indices_notes

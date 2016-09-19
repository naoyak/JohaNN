import numpy as np
from music21 import midi, stream

def __sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def __predict(model, x, indices_notes, temperature):
    preds = model.predict(x, verbose=0)[0]
    next_index = __sample(preds, temperature)
    next_val = indices_notes[next_index]

    return next_val

def generate_sequence(model, seq_len, melody_corpus, melody_set, phrase_len, notes_indices, indices_notes, temperature):
    gen_melody_indices = np.zeros((1, phrase_len, len(melody_set)))
    start_pos = np.random.randint(0, len(melody_corpus) - phrase_len)
    seed_phrase = melody_corpus[start_pos : start_pos + phrase_len]
    gen_melody = seed_phrase


    for _ in range(seq_len):
        seed_phrase = gen_melody[-phrase_len:]
        for i, note in enumerate(seed_phrase):
            gen_melody_indices[0, i, notes_indices[note]] = 1
        x = gen_melody_indices
        next_note = __predict(model, x, indices_notes, temperature)
        # seed_phrase.append(next_note)
        gen_melody.append(next_note)
        # seed_phrase = seed_phrase[1:]

#     gen_melody = [indices_notes[i] for i in gen_melody_indices]
    return gen_melody

def play_melody(gen_melody):
    v = stream.Voice()
    last_note_duration = 0
    for n in gen_melody:
        if n[0] == 0:
            new_note = note.Rest()
        else:
            new_pitch = pitch.Pitch()
            # new_pitch.midi = 59.0 + n[0] - 24
            new_pitch.midi = n[0]
            new_note = note.Note(new_pitch)
        new_note.offset = v.highestOffset + last_note_duration
        new_note.duration.quarterLength = n[2]
        last_note_duration = new_note.duration.quarterLength
        v.insert(new_note)

    sp = midi.realtime.StreamPlayer(v)
    sp.play()

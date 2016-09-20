import numpy as np
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.callbacks import History, ModelCheckpoint
from keras.optimizers import RMSprop

from corpus import build_corpus



def train_model(midi_files, save_path, model_path=None, step_size=3, phrase_len=20, layer_size=128, batch_size=128, nb_epoch=1):

    melody_corpus, melody_set, notes_indices, indices_notes = build_corpus(midi_files)

    corpus_size = len(melody_set)

    # cut the corpus into semi-redundant sequences of max_len values
    # step_size = 3
    # phrase_len = 20
    phrases = []
    next_notes = []
    for i in range(0, len(melody_corpus) - phrase_len, step_size):
        phrases.append(melody_corpus[i: i + phrase_len])
        next_notes.append(melody_corpus[i + phrase_len])
    print('nb sequences:', len(phrases))

    # transform data into binary matrices
    X = np.zeros((len(phrases), phrase_len, corpus_size), dtype=np.bool)
    y = np.zeros((len(phrases), corpus_size), dtype=np.bool)
    for i, phrase in enumerate(phrases):
        for j, note in enumerate(phrase):
            X[i, j, notes_indices[note]] = 1
        y[i, notes_indices[next_notes[i]]] = 1
    if model_path is None:
        model = Sequential()
        model.add(LSTM(layer_size, return_sequences=True, input_shape=(phrase_len, corpus_size)))
        model.add(Dropout(0.2))
        model.add(LSTM(layer_size, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(corpus_size))
        model.add(Activation('softmax'))

        model.compile(loss='categorical_crossentropy', optimizer=RMSprop())

    else:
        model = load_model(model_path)

    checkpoint = ModelCheckpoint(filepath=save_path,
        verbose=1, save_best_only=False)
    history = History()
    model.fit(X, y, batch_size=batch_size, nb_epoch=nb_epoch, callbacks=[checkpoint, history])

    return model, melody_corpus, melody_set, notes_indices, indices_notes

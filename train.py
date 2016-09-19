import numpy as np
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.callbacks import History, ModelCheckpoint
from keras.optimizers import RMSprop

from corpus import build_corpus



def train_bach_corpus(save_path, model_path=None, batch_size=128, nb_epoch=1):
    midi_files = []
    for suite in ['1007', '1008', '1009', '1010', '1011', '1012']:
        for mvt in ['1', '2', '3', '4', '5', '6']:
            filename = 'bach_suites/bwv{}_0{}.mid'.format(suite, mvt)
            midi_files.append(filename)
    # with open('midi_files') as filelist:
    #     for f in filelist:
    #         midi_files.append(f.replace('\n', ''))

    melody_corpus, melody_set, notes_indices, indices_notes = build_corpus(midi_files)

    corpus_size = len(melody_set)

    # cut the corpus into semi-redundant sequences of max_len values
    step_size = 3
    phrase_len = 20
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
        model.add(LSTM(512, return_sequences=True, input_shape=(phrase_len, corpus_size)))
        model.add(Dropout(0.2))
        model.add(LSTM(512, return_sequences=False))
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

    return model

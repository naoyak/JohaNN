import pickle
from pathlib import Path
from train import train_model

midi_files = []
for suite in ['1007', '1008', '1009', '1010', '1011', '1012']:
    for mvt in ['1', '2', '3', '4', '5', '6']:
        filename = 'bach_suites/bwv{}_0{}.mid'.format(suite, mvt)
        midi_files.append(filename)

phrase_lengths = [10, 20, 35, 50]
layer_size = 512
step_size = 3
batch_size = 256
nb_epoch = 700

corpus_data = {}

for phrase_len in phrase_lengths:
    param_str = '{}_{}_{}'.format(step_size, phrase_len, layer_size)
    save_path = 'model_save/bach_model_{}.h5'.format(param_str)
    model_path = save_path if Path(save_path).is_file() else None

    model, melody_corpus, melody_set, notes_indices, indices_notes = train_model(midi_files, save_path, model_path, step_size, phrase_len, layer_size)
    corpus = (melody_corpus, melody_set, notes_indices, indices_notes)

    with open ('corpus/corpus_{}.pkl'.format(param_str), 'wb') as f:
        pickle.dump(corpus, f, pickle.HIGHEST_PROTOCOL)

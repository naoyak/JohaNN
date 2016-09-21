from flask import Flask, request, render_template, jsonify
from flask_bootstrap import Bootstrap
from keras.models import load_model
import boto3

from forms import JohannForm
from generate import generate_sequence, play_melody
from utils import unpack_corpus, create_png_from_stream, create_midi_from_stream, upload_to_s3_bucket
from midi_audio import to_audio

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'devkey'

app.config.from_object(__name__)

phrase_lengths = [10, 20, 35, 50]
layer_size = 512
step_size = 3

AWS_BUCKET_NAME = 'naoya-metis'

model_data = {
    'corpus': unpack_corpus('corpus/bach_suites_corpus.pkl'),
    'models': {}
}

for phrase_len in phrase_lengths:
    model_data['models']['len_{}'.format(phrase_len)] = load_model('model_save/bach_model_{}_{}_{}.h5'.format(step_size, phrase_len, layer_size))


@app.route('/generate/', methods=["POST"])
def generate():
    """
    Accepts a POST request with parameters and generates a musical fragment.
    """
    data = request.json
    melody_corpus, melody_set, notes_indices, indices_notes = model_data['corpus']
    temperature = float(data['temperature'])
    phrase_len = int(data['seed_length'])
    seq_len = int(data['seq_len'])
    model = model_data['models']['len_{}'.format(str(phrase_len))]
    songname = data['song_name']

    melody = generate_sequence(model, seq_len, melody_corpus, melody_set, phrase_len, notes_indices, indices_notes, temperature)
    stream = play_melody(melody)
    create_midi_from_stream(stream, songname)
    midi_upload_path = upload_to_s3_bucket('static/tmp/{}.mid'.format(songname), '{}.mid'.format(songname), AWS_BUCKET_NAME)
    png_path = create_png_from_stream(stream, songname)
    png_upload_path = upload_to_s3_bucket('static/tmp/{}.png'.format(songname), '{}.png'.format(songname), AWS_BUCKET_NAME)
    # midi_file = to_audio('soundfont/fluid.sf2', 'tmp/{}.mid'.format(songname), 'tmp/', out_type='mp3')

    return jsonify(midi_s3_path=midi_upload_path, img_s3_path=png_upload_path)

@app.route('/', methods=['GET'])
def main_page():
    data = request.json
    form = JohannForm()
    return render_template("index.html", form=form)

def main(host="0.0.0.0", port=9000, debug=True):
    print('Starting app...')
    app.run(host=host, port=port,debug=debug)

if __name__ == '__main__':
    main()

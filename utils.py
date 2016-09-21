import os
import shutil
import pickle
import boto3
from music21 import midi, converter
from music21.ipython21 import objects as ipythonObjects

AWS_URL_PREFIX = 'https://s3-us-west-2.amazonaws.com/'

s3 = boto3.resource('s3')

def unpack_corpus(filename):
    with open(filename, 'rb') as f:
        corpus = pickle.load(f)
    return corpus

def create_midi_from_stream(stream, filename):
    mf = midi.translate.streamToMidiFile(stream)
    mf.open('static/tmp/{}.mid'.format(filename), 'wb')
    mf.write()
    mf.close()

def create_png_from_stream(stream, filename):
    helperFormat = 'musicxml'
    helperSubformats = ['png']
    helperConverter = converter.Converter()
    helperConverter.setSubconverterFromFormat(helperFormat)
    helperSubConverter = helperConverter.subConverter

    # if helperFormat == 'musicxml':
    #     ### hack to make musescore excerpts -- fix with a converter class in MusicXML
    #     savedDefaultTitle = defaults.title
    #     savedDefaultAuthor = defaults.author
    #     defaults.title = ''
    #     defaults.author = ''

    #     if 'Opus' not in obj.classes:
    fp = helperSubConverter.write(stream, helperFormat, subformats=helperSubformats)

    # defaults.title = savedDefaultTitle
    # defaults.author = savedDefaultAuthor
    if helperSubformats[0] == 'png':
        ipo = ipythonObjects.IPythonPNGObject(fp)
    target_filename = os.path.join(os.getcwd(), "static/tmp/{}.png".format(filename))
    shutil.move(ipo.fp, target_filename)
    return(target_filename)


def upload_to_s3_bucket(local_path, upload_path, bucket):
    # Upload a new file
    s3.Object(bucket, upload_path).put(Body=open(local_path, 'rb'))
    return AWS_URL_PREFIX + bucket + '/' + upload_path

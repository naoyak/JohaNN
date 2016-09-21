from flask_wtf import Form
from wtforms import DecimalField, IntegerField, SelectField, SubmitField, StringField
from wtforms.validators import DataRequired, Length

class JohannForm(Form):
    temperature = DecimalField('Temperature', validators=[DataRequired()])
    seed_length = SelectField('Seed Length', choices=[(10, 10), (20, 20), (35, 35), (50, 50)])
    seq_len = IntegerField('Fragment Length', validators=[DataRequired()])
    song_name = StringField('Name Your Piece', validators=[DataRequired(), Length(min=4, max=25)])
    submit = SubmitField('Generate Music! ♫')

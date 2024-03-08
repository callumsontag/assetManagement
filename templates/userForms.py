from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    email = StringField('Name', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    firstName = StringField('FirstName', validators=[DataRequired()])
    lastName = StringField('LastName', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Name', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AssetForm(FlaskForm):
    asset = StringField('Asset', validators=[DataRequired()])
    assetDescription = StringField(
        'AssetDescription', validators=[DataRequired()])
    submit = SubmitField('Submit')

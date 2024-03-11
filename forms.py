from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email


class CustomEmailValidation:
    def __call__(self, form, field):
        if not field.data.endswith('@mettle.co.uk'):
            raise ValidationError('Email address must be @mettle.co.uk')


class SecurePasswordValidator:
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True, require_digit=True, require_special=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special

    def __call__(self, form, field):
        password = field.data
        if len(password) < self.min_length:
            raise ValidationError(
                f'Password must be at least {self.min_length} characters long')
        if self.require_uppercase and not any(char.isupper() for char in password):
            raise ValidationError(
                'Password must contain at least one uppercase letter')
        if self.require_lowercase and not any(char.islower() for char in password):
            raise ValidationError(
                'Password must contain at least one lowercase letter')
        if self.require_digit and not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit')
        if self.require_special and not any(not char.isalnum() for char in password):
            raise ValidationError(
                'Password must contain at least one special character')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Email(), CustomEmailValidation()])
    password = PasswordField('Password', validators=[
                             DataRequired(), SecurePasswordValidator()])
    firstName = StringField('FirstName', validators=[DataRequired()])
    lastName = StringField('LastName', validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Name', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AssetForm(FlaskForm):
    asset = StringField('Asset', validators=[DataRequired()])
    assetDescription = TextAreaField(
        'AssetDescription', validators=[DataRequired()])
    submit = SubmitField('Submit')

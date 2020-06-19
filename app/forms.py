from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Optional
from app.models import User, Project

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('PLease use a different email address.')

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    budget = FloatField('Total Budget')
    submit = SubmitField('Add Project')

    def validate_project_name(self, name):
        name = Project.query.filter_by(name=name.data).first()
        if name is not None:
            raise ValidationError('This project name is already in use.')

class VendorForm(FlaskForm):
    name = StringField('Vendor Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number')
    email = StringField('Email Address')
    submit = SubmitField('Add Vendor')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class AddTransactionForm(FlaskForm):
    vendor = StringField('Vendor Name', validators=[DataRequired()])
    date = DateField('Transaction Date', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Transaction')

class AddInvoiceForm(FlaskForm):
    vendor = StringField('Vendor Name', validators=[DataRequired()])
    invoice_date = DateField('Invoice Date', validators=[DataRequired()])
    paid_date = DateField('Date Paid', validators=[Optional()])
    amount = FloatField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Transaction')

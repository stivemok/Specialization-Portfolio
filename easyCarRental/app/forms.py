from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User
from wtforms import DateField
from wtforms import SelectMultipleField
from wtforms import BooleanField
from wtforms import BooleanField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        

class CarRentalForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()], render_kw={"pattern": "[a-zA-Z]+", "required": True})
    mname = StringField('Middle Name', validators=[DataRequired()], render_kw={"pattern": "[a-zA-Z]+", "required": True})
    lname = StringField('Last Name', validators=[DataRequired()], render_kw={"pattern": "[a-zA-Z]+", "required": True})
    idpassport = FileField('ID/Passport', validators=[DataRequired()], render_kw={"accept": "image/*", "required": True})
    phone = StringField('Phone Number', validators=[DataRequired()], render_kw={"pattern": "\d{10}", "required": True})
    carreg = FileField('Car Registration', validators=[DataRequired()], render_kw={"accept": "image/*", "required": True})
    photo1 = FileField('Car Photo 1', validators=[DataRequired()], render_kw={"accept": "image/*", "required": True})
    photo2 = FileField('Car Photo 2', validators=[DataRequired()], render_kw={"accept": "image/*", "required": True})
    email = StringField('Email Address', validators=[DataRequired(), Email()], render_kw={"required": True})
    PlateNo = StringField('Plate Number', validators=[DataRequired()], render_kw={"required": True})
    make = StringField('Make', validators=[DataRequired()], render_kw={"required": True})
    model = StringField('Model', validators=[DataRequired()], render_kw={"required": True})
    color = StringField('Color', validators=[DataRequired()], render_kw={"required": True})
    price = StringField('Price', validators=[DataRequired()], render_kw={"required": True})
    condition = StringField('Condition', validators=[DataRequired()], render_kw={"required": True})
    vehicle = SelectField('Vehicle Type', choices=[('sedan', 'Sedan'), ('suv', 'SUV'), ('truck', 'Truck'), ('van', 'Van')], validators=[DataRequired()])
    year = IntegerField('Release Year', validators=[DataRequired()], render_kw={"min": "1900", "max": "2023", "required": True})
    submit = SubmitField('Submit')


class VehicleSearchForm(FlaskForm):
    sedan = BooleanField('Sedan')
    compact = BooleanField('Compact')
    suv = BooleanField('SUV')
    truck = BooleanField('Truck')
    van = BooleanField('Van')
    submit = SubmitField('Search Vehicle')

class CarInformationForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired()], render_kw={"required": True})
    model = StringField('Model', validators=[DataRequired()], render_kw={"required": True})
    year = IntegerField('Release Year', validators=[DataRequired()], render_kw={"min": "1900", "max": "2023", "required": True})
    condition = StringField('Condition', validators=[DataRequired()], render_kw={"required": True})
    color = StringField('Color', validators=[DataRequired()], render_kw={"required": True})
    price = StringField('Price', validators=[DataRequired()], render_kw={"required": True})
    photo1 = FileField('Photo 1', validators=[DataRequired()], render_kw={"accept": "image/*", "required": True})
    photo2 = FileField('Photo 2', validators=[DataRequired()], render_kw={"accept": "image/*", "required": True})
    PlateNo = StringField('PlateNo', validators=[DataRequired()], render_kw={"required": True})
    vehicle = SelectField('Vehicle Type', choices=[('sedan', 'Sedan'), ('compact', 'Compact'), ('suv', 'SUV'), ('truck', 'Truck'), ('van', 'Van')], validators=[DataRequired()])
    submit = SubmitField('Submit')


class RemoveCarForm(FlaskForm):
    selected_cars = SelectMultipleField('Select Cars', coerce=str)
    submit = SubmitField('Remove Selected Cars')


class CarUpdateForm(FlaskForm):
    plate_no = StringField('Plate Number', validators=[DataRequired()])
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    vehicle = StringField('Vehicle', validators=[DataRequired()])
    photo1 = FileField('Photo 1')
    photo2 = FileField('Photo 2')
    submit = SubmitField('Update Car')

class BookVehicleForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(max=32)])
    mname = StringField('Middle Name', validators=[DataRequired(), Length(max=32)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(max=32)])
    idpassport = FileField('ID/Passport/Driving licence', validators=[DataRequired()], render_kw={"accept": "image/*", "required": True})
    pickup = DateField('Pickup Date', format='%Y-%m-%d', validators=[DataRequired()])
    pickup_location = SelectField('Pickup Location', choices=[('Easy Rentals Office', 'Easy Rentals Office'), ('ADD Airport', 'ADD Airport')], validators=[DataRequired()])
    dropoff = DateField('Dropoff Date', format='%Y-%m-%d', validators=[DataRequired()])
    dropoff_location = SelectField('Drop-off Location', choices=[('Easy Rentals Office', 'Easy Rentals Office'), ('ADD Airport', 'ADD Airport')], validators=[DataRequired()])
    vehicle_type = SelectField('Vehicle Type', choices=[('sedan', 'Sedan'), ('compact', 'Compact'), ('suv', 'SUV'), ('truck', 'Truck'), ('van', 'Van')], validators=[DataRequired()])
    PaymentMethod = StringField('Payment Method', validators=[DataRequired(), Length(max=32)])
    submit = SubmitField('Book Vehicle')
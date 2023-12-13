from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, CarRentalForm
from app.models import User, FormData, Car
from datetime import datetime
from app.forms import VehicleSearchForm, CarInformationForm, RemoveCarForm, CarUpdateForm
from app.api.api_routes import get_cars
import base64
import requests


@app.route('/')
@app.route('/index')
def index():
    form = VehicleSearchForm()
    return render_template("index.html", title='Home Page', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('admin')
            flash(f'Successfully logged in as {user.username}', 'success')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/admin')
@login_required
def admin():
    return render_template("AdminPage.html", title='ADMIN Page')

@app.route('/VehicelRegistration', methods=['GET', 'POST'])
def VehicelRegistration():
    form = CarRentalForm()

    if form.validate_on_submit():
        # Check if the plate number already exists in the database
        existing_entry = FormData.query.filter_by(PlateNo=form.PlateNo.data).first()

        if existing_entry:
            flash('the car is already registered. Please register another', 'error')
        else:
            # Read the photo data once
            photo1_data = form.photo1.data.read()
            photo2_data = form.photo2.data.read()

            # If no duplicate plate number, create a new entry in the database
            new_entry = FormData(
                fname=form.fname.data,
                mname=form.mname.data,
                lname=form.lname.data,
                phone=form.phone.data,
                email=form.email.data,
                vehicle=form.vehicle.data,
                year=form.year.data,
                idpassport=form.idpassport.data.read(),
                carreg=form.carreg.data.read(),
                photo1=photo1_data,
                photo2=photo2_data,
                PlateNo=form.PlateNo.data,
                make=form.make.data,
                model=form.model.data,
                color=form.color.data,
                price=form.price.data,
                condition=form.condition.data,
                submissionDate=datetime.utcnow()
            )

            db.session.add(new_entry)
            db.session.commit()

            # Check if a Car object with the same Plate number already exists in the Car table
            existing_car = Car.query.filter_by(PlateNo=form.PlateNo.data).first()

            if not existing_car:
                # If a Car object with the same Plate number does not exist, create a new Car object with the form data
                new_car = Car(
                    make=form.make.data,
                    model=form.model.data,
                    year=form.year.data,
                    condition=form.condition.data,
                    color=form.color.data,
                    price=form.price.data,
                    photo1=photo1_data,
                    photo2=photo2_data,
                    PlateNo=form.PlateNo.data,
                    vehicle=form.vehicle.data
                )

                db.session.add(new_car)
                db.session.commit()

            flash('Successfully registered your car!', 'success')
            return redirect(url_for('VehicelRegistration'))

    return render_template("VehicelRegistration.html", title='VehicelRegistration', form=form)








@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/location')
def location():
    return render_template('location.html')


@app.route('/vehicles', methods=['GET'])
def vehicles():
    # Make a request to the API endpoint (/api/cars)
    api_url = 'http://localhost:3000/api/cars'

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Include any necessary query parameters in the API request
    api_params = {'page': page, 'per_page': per_page}
    response = requests.get(api_url, params=api_params)

    if response.status_code == 200:
        # If the API request is successful, extract data from the JSON response
        api_data = response.json()
        cars = api_data.get('cars', [])
        total_pages = api_data.get('total_pages', 1)
        current_page = api_data.get('current_page', 1)
    else:
        # If the API request fails, handle the error
        return render_template('error.html', error_message='Failed to fetch data from the API')

    # Render the template using data from the API
    return render_template('vehicles.html', cars=cars, total_pages=total_pages, current_page=current_page)

@app.route('/AddCar', methods=['GET', 'POST'])
@login_required
def AddCar():
    form = CarInformationForm()
    if form.validate_on_submit():
         # Check if a Car object with the same Plate number already exists in the Car table
            existing_car = Car.query.filter_by(PlateNo=form.PlateNo.data).first()

            if not existing_car:
                # If a Car object with the same Plate number does not exist, create a new Car object with the form data
                new_car = Car(
                    make=form.make.data,
                    model=form.model.data,
                    year=form.year.data,
                    condition=form.condition.data,
                    color=form.color.data,
                    price=form.price.data,
                    photo1=form.photo1.data.read(),
                    photo2=form.photo2.data.read(),
                    PlateNo=form.PlateNo.data,
                    vehicle=form.vehicle.data
                )

                db.session.add(new_car)
                db.session.commit()

            flash('Successfully add a car!', 'success')
            return redirect(url_for('VehicelRegistration'))
    return render_template('AddCar.html', title='add car', form=form)


@app.route('/UserInfo')
def UserInfo():
    # Make a request to the API endpoint (/api/registrations)
    api_url = 'http://localhost:3000/api/registrations'  # Update the API endpoint
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Include any necessary query parameters in the API request
    api_params = {'page': page, 'per_page': per_page}
    response = requests.get(api_url, params=api_params)

    if response.status_code == 200:
        # If the API request is successful, extract data from the JSON response
        api_data = response.json()
        registrations = api_data.get('registrations', [])
        total_pages = api_data.get('pagination', {}).get('total_pages', 1)
        current_page = api_data.get('pagination', {}).get('current_page', 1)
    else:
        # If the API request fails, handle the error (e.g., show an error page)
        return render_template('error.html', error_message='Failed to fetch data from the API')

    # Render the template using data from the API
    return render_template('UserInfo.html', registrations=registrations, total_pages=total_pages, current_page=current_page)


@app.route('/remove_car', methods=['GET', 'POST'])
@login_required
def remove_car():
    form = RemoveCarForm()
    page = request.args.get('page', 1, type=int)
    cars = Car.query.paginate(page=page, per_page=5)
    form.selected_cars.choices = [(car.PlateNo, car.PlateNo + ' ' + car.model) for car in cars.items]
    if form.validate_on_submit():
        selected_cars = form.selected_cars.data
        for plateNo in selected_cars:
            car = Car.query.filter_by(PlateNo=plateNo).first()
            if car:
                db.session.delete(car)
                db.session.commit()
        flash('Successfully removed selected cars!', 'success')
        return redirect(url_for('remove_car'))
    return render_template('remove_car.html', title='remove car', form=form, cars=cars)




@app.route('/UpdateCar', methods=['GET', 'POST'])
@login_required
def UpdateCar():
    form = CarUpdateForm()

    # Fetch all available cars
    cars = Car.query.all()

    if form.validate_on_submit():
        # Fetch the selected car by its PlateNo
        selected_plate_no = form.plate_no.data
        selected_car = Car.query.filter_by(PlateNo=selected_plate_no).first_or_404()

        # Update the selected car with the form data
        form.populate_obj(selected_car)

        # Handle photo updates if needed
        if form.photo1.data:
            selected_car.photo1 = form.photo1.data.read()
        if form.photo2.data:
            selected_car.photo2 = form.photo2.data.read()

        db.session.commit()

        flash('Car updated successfully!', 'success')
        return redirect(url_for('UpdateCar'))

    return render_template('UpdateCar.html', title='Update Car', form=form, cars=cars)

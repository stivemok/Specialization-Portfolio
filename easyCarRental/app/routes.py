<<<<<<< HEAD
from app import app
=======
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, CarRentalForm
from app.models import User, FormData
from datetime import datetime
from app.forms import VehicleSearchForm
from app.api.api_routes import get_cars
import base64
import requests

>>>>>>> 74564bc0f1cd9eaa1d9d24e5f983702f9cd5d961

@app.route('/')
@app.route('/index')
def index():
<<<<<<< HEAD
    user = {'username': 'Stive'}
    return '''
<html>
    <header>
        <title>Home page - Easy Rentals</title>
    </header>
    <body>
        <h1>Hello, ''' + user['username'] + '''!</h1>
    </body>
</html>'''
=======
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
                photo1=form.photo1.data.read(),
                photo2=form.photo2.data.read(),
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
    api_url = 'http://localhost:5000/api/cars'  # Replace with the actual URL of your API
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
        # If the API request fails, handle the error (e.g., show an error page)
        return render_template('error.html', error_message='Failed to fetch data from the API')

    # Render the template using data from the API
    return render_template('vehicles.html', cars=cars, total_pages=total_pages, current_page=current_page)

@app.route('/all_entries', methods=['GET'])
def display_all_entries():
    # Retrieve all entries from the database
    all_entries = FormData.query.all()

    # Render the entries on a new page
    return render_template("all_entries.html", title='All Entries', entries=all_entries)
>>>>>>> 74564bc0f1cd9eaa1d9d24e5f983702f9cd5d961

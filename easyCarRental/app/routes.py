from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, CarRentalForm
from app.models import User, FormData, Car, Booking, VehicleCount
from datetime import datetime
from app.forms import VehicleSearchForm, CarInformationForm, RemoveCarForm, CarUpdateForm 
from app.forms import BookVehicleForm, UpdateUserForm
from flask import jsonify
import base64
import requests
import logging
from wtforms import BooleanField
from app.api.api_routes import submit_payment,  get_cars, get_registrations
from flask import current_app
from flask import Flask, render_template
import plotly
import plotly.graph_objs as go
import json



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
    user_count = User.query.count()
    cars_count = Car.query.count()
    # app.logger.info(f"Usersssssssssssss: {user_count}")
    graphs = [
        go.Figure(
            data=[go.Bar(y=[2,1,3])],
            layout_title_text="Vehicle Count"
        ),
        # go.Figure(
        #     data=[go.Scatter(y=[4,2,5], mode='lines')],
        #     layout_title_text="Number of Users"
        # ),
        go.Figure(
            data=[go.Pie(labels=["Sedan", "Suv", "Label3"], values=[3,2,1])],
            layout_title_text="Number Of Cars"
        )
        ]
    graphJSON = [json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder) for graph in graphs]


    return render_template("AdminPage.html", title='ADMIN Page', graphs=graphJSON, user_count=user_count, total_cars=cars_count)

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
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Call the function that handles the /api/cars endpoint
    response = get_cars(page, per_page)
    api_data = response.get_json()

    cars = api_data.get('cars', [])
    cars_count = cars.__len__()
    total_pages = api_data.get('total_pages', 1)
    app.logger.info(f"Total pages: {total_pages}")
    app.logger.info(f"cars : {cars}")
    current_page = api_data.get('current_page', 1)

    # Render the template using data from the API
    return render_template('vehicles.html', cars=cars, total_pages=total_pages, current_page=current_page)


@app.route('/AddCar', methods=['GET', 'POST'])
@login_required
def AddCar():
    form = CarInformationForm()
    if form.validate_on_submit():
        existing_car = Car.query.filter_by(PlateNo=form.PlateNo.data).first()
        if existing_car:
            flash('This car is already registered!', 'error')
            return render_template('AddCar.html', title='add car', form=form)

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

        vehicle_count = VehicleCount.query.filter_by(vehicle_type=new_car.vehicle).first()
        if not vehicle_count:
            vehicle_count = VehicleCount(vehicle_type=new_car.vehicle, count=1)
            db.session.add(vehicle_count)
        else:
            vehicle_count.count += 1

        db.session.commit()

        flash('Successfully added a car!', 'success')
        return redirect(url_for('AddCar'))

    return render_template('AddCar.html', title='add car', form=form)


@app.route('/UserInfo', methods=['GET'])
def UserInfo():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Call the function that handles the /api/registrations endpoint
    response = get_registrations()
    api_data = response.get_json()

    registrations = api_data.get('registrations', [])
    total_pages = api_data.get('pagination', {}).get('total_pages', 1)
    current_page = api_data.get('pagination', {}).get('current_page', 1)

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
                # Check if the car is already booked
                if Booking.query.filter_by(VehicleId=car.VehicleId).first():
                    flash(f'The car {car.PlateNo} is already booked and cannot be removed.', 'danger')
                    continue  # Skip to the next iteration

                # If the car is not booked, proceed with removal
                vehicle_count = VehicleCount.query.filter_by(vehicle_type=car.vehicle).first()
                if vehicle_count and vehicle_count.count > 0:
                    vehicle_count.count -= 1

                db.session.delete(car)
                flash('Successfully removed selected cars!', 'success')

        db.session.commit()

        
        return redirect(url_for('remove_car'))

    return render_template('remove_car.html', title='Remove Car', form=form, cars=cars)


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


@app.route('/SearchVehicle', methods=['GET', 'POST'])
def SearchVehicle():
    form = VehicleSearchForm()

    if form.validate_on_submit():
        vehicle_types = [field.label.text.lower() for field in form if isinstance(field, BooleanField) and field.data]

        # Query the database for the vehicle
        page = request.args.get('page', 1, type=int)
        per_page = 10
        vehicles = Car.query.filter(Car.vehicle.in_(vehicle_types)).paginate(page=page, per_page=per_page)

        if vehicles.items:
            vehicles_list = []
            for vehicle in vehicles.items:
                try:
                    # Convert the binary data to an image file
                    photo1_base64 = base64.b64encode(vehicle.photo1).decode('utf-8') if vehicle.photo1 else None
                    photo2_base64 = base64.b64encode(vehicle.photo2).decode('utf-8') if vehicle.photo2 else None

                    # Create a dictionary with vehicle details
                    vehicle_details = {
                        'vehicle': vehicle.vehicle,
                        'year': vehicle.year,
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'color': vehicle.color,
                        'price': vehicle.price,
                        'condition': vehicle.condition,
                        'photo1': photo1_base64,
                        'photo2': photo2_base64,
                        'VehicleId': vehicle.VehicleId,
                        'available': vehicle.available,
                    }
                    vehicles_list.append(vehicle_details)
                except Exception as e:
                    logging.error(f"Error encoding photos for vehicle {vehicle.VehicleId}: {e}")

            result = {
                'vehicles': vehicles_list,
                'total_pages': vehicles.pages,
                'current_page': vehicles.page,
                'per_page': vehicles.per_page,
                'total_vehicles': vehicles.total
            }

            return render_template('VehicleSearch.html', title='Search Vehicle', form=form, cars=result['vehicles'], total_pages=result['total_pages'], current_page=result['current_page'])

        else:
            # Vehicle not found
            flash('No vehicle found! Please check these cars.', 'info')
            return redirect(url_for('vehicles'))

    return render_template('VehicleSearch.html', title='Search Vehicle', form=form)


@app.route('/BookVehicle/<int:vehicle_id>/<vehicle_type>', methods=['GET', 'POST'])
def BookVehicle(vehicle_id, vehicle_type):
    form = BookVehicleForm()
    car = Car.query.get(vehicle_id)

    if not car:
        flash('Vehicle not found.')
        return redirect(url_for('BookVehicle'))

    if form.validate_on_submit():
        
        try:
            vehicle_type = form.vehicle_type.data
            idpassport_data = form.idpassport.data.read()

            existing_booking = Booking.query.filter(
                Booking.VehicleId == vehicle_id,
                Booking.pickup_date <= form.dropoff.data,
                Booking.dropoff_date >= form.pickup.data,
            ).first()

            if not car.available or existing_booking:
                flash('The car is not available. Please check another vehicle or date.')
                

            payment_method_result = submit_payment(form.PaymentMethod.data)
            flash(f'Payment Result: {payment_method_result}')

            booking = Booking(
                pickup_date=form.pickup.data,
                pickup_location=form.pickup_location.data,
                dropoff_date=form.dropoff.data,
                dropoff_location=form.dropoff_location.data,
                vehicle_type=form.vehicle_type.data,
                fname=form.fname.data,
                mname=form.mname.data,
                lname=form.lname.data,
                idpassport=idpassport_data,
                PaymentMethod=form.PaymentMethod.data,
                VehicleId=vehicle_id
            )
            db.session.add(booking)

            car.available = False
            vehicle_count = VehicleCount.query.filter_by(vehicle_type=form.vehicle_type.data).first()
             

            if vehicle_count:
                vehicle_count.count -= 1

            db.session.commit()
            flash('Successfully booked')
            return redirect(url_for('BookVehicle', vehicle_id=vehicle_id, vehicle_type=vehicle_type))

        except Exception as e:
            current_app.logger.error(f'Error occurred: {e}')
            print(f'Error occurred: {e}')  # Add this line for debugging
            db.session.rollback()
            flash('An error occurred. Database session rolled back.')

    return render_template('BookVehicle.html', form=form, car=car)


@app.route('/vehicle_count', methods=['GET'])
@login_required
def vehicle_count():
    counts = VehicleCount.query.all()
    return render_template('vehicle_count.html', title='Avaliable Vehicles', counts=counts)


@app.route('/BookedVehicle', methods=['GET', 'POST'])
@login_required
def BookedVehicle():
    if request.method == 'POST':
        # Get the list of booking IDs from the form submission
        booking_ids = request.form.getlist('booking_ids')

        # Get the bookings to be deleted
        bookings_to_delete = Booking.query.filter(Booking.id.in_(booking_ids))

        # Update the vehicle count and availability for each booking to be deleted
        for booking in bookings_to_delete:
            vehicle_count = VehicleCount.query.filter_by(vehicle_type=booking.vehicle_type).first()
            if vehicle_count:
                vehicle_count.count += 1

            # Fetch the car from the Car table and update its availability
            car = Car.query.get(booking.VehicleId)
            if car:
                car.available = True 
                db.session.add(car)  # Add the car to the session to track changes

        # Delete the selected bookings from the database
        bookings_to_delete.delete(synchronize_session=False)
        db.session.commit()

        # Redirect back to the BookedVehicle page
        return redirect(url_for('BookedVehicle'))

    # Get the page number from the request arguments
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Query the database for all bookings and related Car information
    bookings = Booking.query.options(db.joinedload(Booking.car)).paginate(page=page, per_page=per_page)


    bookings_list = []
    for booking in bookings.items:
        try:
            # Convert the binary data to an image file
            idpassport_base64 = base64.b64encode(booking.idpassport).decode('utf-8') if booking.idpassport else None
            plate_no = booking.car.PlateNo if booking.car else None

            # Create a dictionary with booking details
            booking_details = {
                'id': booking.id,
                'pickup_date': booking.pickup_date,
                'pickup_location': booking.pickup_location,
                'dropoff_date': booking.dropoff_date,
                'dropoff_location': booking.dropoff_location,
                'vehicle_type': booking.vehicle_type,
                'fname': booking.fname,
                'mname': booking.mname,
                'lname': booking.lname,
                'idpassport': idpassport_base64,
                'PaymentMethod': booking.PaymentMethod,
                'vehicle_id': booking.VehicleId,
                'plate_no': plate_no,  # Include PlateNo in the result
            }
            bookings_list.append(booking_details)
        except Exception as e:
            logging.error(f"Error encoding passport for booking {booking.id}: {e}")

    result = {
        'bookings': bookings_list,
        'total_pages': bookings.pages,
        'current_page': bookings.page,
        'per_page': bookings.per_page,
        'total_bookings': bookings.total
    }

    return render_template('BookedVehicle.html', title='Booked Vehicle', bookings=result['bookings'], total_pages=result['total_pages'], current_page=result['current_page'])


@app.route('/delete_registrations', methods=['POST'])
@login_required
def delete_registrations():
    # Get the list of registration IDs to delete from the form data
    registration_ids = request.form.getlist('registration_ids')

    # Query the database for the registrations and delete them
    for registration_id in registration_ids:
        registration = FormData.query.get(registration_id)
        if registration:
            db.session.delete(registration)

    # Commit the changes to the database
    db.session.commit()

    # Redirect the user back to the UserInfo page
    return redirect(url_for('UserInfo'))



@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
        return redirect(url_for('users'))
    else:
        users = User.query.all()
        return render_template('users.html', title='Users', users=users)


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    form = UpdateUserForm()
    if form.validate_on_submit():
        user = User.query.get(form.user_id.data)
        if user:
            user.username = form.username.data
            user.email = form.email.data
            user.password = form.password.data  # Consider using a hashed password
            db.session.commit()
        return redirect(url_for('users'))
    return render_template('update_user.html', form=form)
from flask import jsonify, request
from app import app
from app.models import FormData, Car
import base64
import logging


@app.route('/api/cars', methods=['GET'])
def get_cars():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        cars = Car.query.paginate(page=page, per_page=per_page)

        cars_list = []
        for car in cars.items:
            try:
                photo1_base64 = base64.b64encode(car.photo1).decode('utf-8') if car.photo1 else None
                photo2_base64 = base64.b64encode(car.photo2).decode('utf-8') if car.photo2 else None
                cars_list.append({
                    'VehicleId': car.VehicleId,
                    'vehicle': car.vehicle,
                    'year': car.year,
                    'make': car.make,
                    'model': car.model,
                    'color': car.color,
                    'price': car.price,
                    'condition': car.condition,
                    'photo1': photo1_base64,
                    'photo2': photo2_base64,
                    'PlateNo': car.PlateNo,
                    'available': car.available,
                })
            except Exception as e:
                logging.error(f"Error encoding photos for car {car.VehicleId}: {e}")

    except Exception as e:
        logging.error(f"Error retrieving cars: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

    result = {
        'cars': cars_list,
        'total_pages': cars.pages,
        'current_page': cars.page,
        'per_page': cars.per_page,
        'total_cars': cars.total
    }

    return jsonify(result)


@app.route('/api/registrations', methods=['GET'])
def get_registrations():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        registrations = FormData.query.paginate(page=page, per_page=per_page)

        registrations_list = []
        for registration in registrations.items:
            try:
                # Perform base64 encoding for specific fields
                carreg_base64 = base64.b64encode(registration.carreg).decode('utf-8') if registration.carreg else None
                idpassport_base64 = base64.b64encode(registration.idpassport).decode('utf-8') if registration.idpassport else None
                photo1_base64 = base64.b64encode(registration.photo1).decode('utf-8') if registration.photo1 else None
                photo2_base64 = base64.b64encode(registration.photo2).decode('utf-8') if registration.photo2 else None
            
                registrations_list.append({
                    'CustomerId': registration.CustomerId,
                    'fname': registration.fname,
                    'mname': registration.mname,
                    'lname': registration.lname,
                    'phone': registration.phone,
                    'email': registration.email,
                    'vehicle': registration.vehicle,
                    'year': registration.year,
                    'PlateNo': registration.PlateNo,
                    'make': registration.make,
                    'model': registration.model,
                    'color': registration.color,
                    'price': registration.price,
                    'condition': registration.condition,
                    'submissionDate': registration.submissionDate.strftime('%Y-%m-%d %H:%M:%S'),
                    'carreg': carreg_base64,
                    'idpassport': idpassport_base64,
                    'photo1': photo1_base64,
                    'photo2': photo2_base64,
                })
            except Exception as e:
                logging.error(f"Error encoding photos for registration {registration.CustomerId}: {e}")

        result = {
            'registrations': registrations_list,
            'pagination': {
                'total_pages': registrations.pages,
                'current_page': registrations.page,
                'per_page': registrations.per_page,
                'total_registrations': registrations.total
            }
        }

        # Add links for next and previous pages
        if registrations.has_prev:
            result['pagination']['prev_page'] = url_for('get_registrations', page=registrations.prev_num, _external=True)
        if registrations.has_next:
            result['pagination']['next_page'] = url_for('get_registrations', page=registrations.next_num, _external=True)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
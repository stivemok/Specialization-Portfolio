from flask import jsonify, request
from app import app
from app.models import FormData
import base64
import logging


@app.route('/api/cars', methods=['GET'])
def get_cars():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        cars = FormData.query.paginate(page=page, per_page=per_page)

        cars_list = []
        for car in cars.items:
            try:
                photo1_base64 = base64.b64encode(car.photo1).decode('utf-8') if car.photo1 else None
                photo2_base64 = base64.b64encode(car.photo2).decode('utf-8') if car.photo2 else None
                cars_list.append({
                    'vehicle': car.vehicle,
                    'year': car.year,
                    'make': car.make,
                    'model': car.model,
                    'color': car.color,
                    'price': car.price,
                    'condition': car.condition,
                    'submissionDate': car.submissionDate.strftime('%Y-%m-%d %H:%M:%S'),
                    'photo1': photo1_base64,
                    'photo2': photo2_base64,
                })
            except Exception as e:
                logging.error(f"Error encoding photos for car {car.id}: {e}")

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
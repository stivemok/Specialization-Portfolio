import os
import unittest
from app import app, db
from app.models import User, FormData, Car, Booking, VehicleCount
from config import Config
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model(self):
        u = User(username='test', email='test@example.com')
        u.set_password('test')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(User.query.filter_by(username='test').first())
        self.assertTrue(u.check_password('test'))
        self.assertFalse(u.check_password('test123'))

    def test_form_data_model(self):
        fd = FormData(fname='John', lname='Doe', email='johndoe@example.com')
        db.session.add(fd)
        db.session.commit()
        self.assertIsNotNone(FormData.query.filter_by(email='johndoe@example.com').first())

    def test_car_model(self):
        c = Car(make='Toyota', model='Corolla', year=2020, price='20000')
        db.session.add(c)
        db.session.commit()
        self.assertIsNotNone(Car.query.filter_by(make='Toyota').first())

    def test_booking_model(self):
        pickup_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
        dropoff_date = datetime.strptime('2022-01-10', '%Y-%m-%d').date()
        b = Booking(pickup_date=pickup_date, dropoff_date=dropoff_date, vehicle_type='Sedan')
        db.session.add(b)
        db.session.commit()
        self.assertIsNotNone(Booking.query.filter_by(vehicle_type='Sedan').first())
    
    def test_vehicle_count_model(self):
        vc = VehicleCount(vehicle_type='Sedan', count=5)
        db.session.add(vc)
        db.session.commit()
        self.assertIsNotNone(VehicleCount.query.filter_by(vehicle_type='Sedan').first())

if __name__ == '__main__':
    unittest.main(verbosity=2)

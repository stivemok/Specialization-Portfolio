from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from sqlalchemy import event, DDL

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class FormData(db.Model):
    __tablename__ = 'vregister'
    CustomerId = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(255))
    mname = db.Column(db.String(255))
    lname = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    email = db.Column(db.String(255))
    vehicle = db.Column(db.String(255))
    year = db.Column(db.Integer)
    idpassport = db.Column(db.LargeBinary((2**32)-1))
    carreg = db.Column(db.LargeBinary((2**32)-1))
    photo1 = db.Column(db.LargeBinary((2**32)-1))
    photo2 = db.Column(db.LargeBinary((2**32)-1))
    PlateNo = db.Column(db.String(255))
    make = db.Column(db.String(255))
    model = db.Column(db.String(255))
    color = db.Column(db.String(255))
    price = db.Column(db.String(255)) 
    condition = db.Column(db.String(255))
    submissionDate = db.Column(db.DateTime)


# Define SQLAlchemy model class for the database table
class Car(db.Model):
    __tablename__ = 'vehicle'
    VehicleId = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(255))
    model = db.Column(db.String(255))
    year = db.Column(db.Integer)
    condition = db.Column(db.String(255))
    price = db.Column(db.String(255))
    color = db.Column(db.String(255))
    photo1 = db.Column(db.LargeBinary((2**32)-1))
    photo2 = db.Column(db.LargeBinary((2**32)-1))
    PlateNo = db.Column(db.String(255))
    vehicle = db.Column(db.String(255))
    available = db.Column(db.Boolean, default=True)


# Define a model for the booking table
class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    pickup_date = db.Column(db.Date, nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    dropoff_date = db.Column(db.Date, nullable=False)
    dropoff_location = db.Column(db.String(255), nullable=False)
    vehicle_type = db.Column(db.String(255), nullable=False)
    fname = db.Column(db.String(255), nullable=False)
    mname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    idpassport = db.Column(db.LargeBinary((2**32)-1))
    PaymentMethod = db.Column(db.String(255), nullable=False)
    

class VehicleCount(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_type = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, default=0)




"""Configuration for Flask application"""
import os
from flask_mail import Mail
basedir = os.path.abspath(os.path.dirname(__file__)) # contain the absolute path of the directory that contains the current file


class Config:
    """
    Config class defining SECRET_KEY and SQLALCHEMY_DATABASE_URI
    SECRET_KEY: Keeps client-side session secure
    SQLALCHEMY_DATABASE_URI: Location of application database
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    # Add Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'eazykiray@gmail.com'
    MAIL_PASSWORD = 'lwpt pgvs jymd cmnw'

    # Initialize Flask-Mail
    mail = Mail()

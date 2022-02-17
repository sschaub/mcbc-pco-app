from flask_sqlalchemy import SQLAlchemy, inspect
from flask import Flask
from config import *

from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def sqlorm_object_as_dict(obj):
    if not obj:
        return None
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

# Define model class
class SchedSpecial(db.Model):
    STATUS_PENDING = 0
    STATUS_APPROVED = 1
    COPYRIGHT_STATUS_UNKNOWN = 0
    COPYRIGHT_STATUS_APPROVED = 1

    id = db.Column(db.Integer, primary_key=True)
    service_type_id = db.Column(db.Integer, nullable=False)   # From PCO
    plan_id = db.Column(db.Integer, nullable=False)           # From PCO
    item_id = db.Column(db.Integer, nullable=False)           # From PCO
    status = db.Column(db.Integer, nullable=False, 
                default=STATUS_PENDING)                       # STATUS_PENDING / STATUS_APPROVED
    version_no =  db.Column(db.Integer, nullable=False, default=1) # Record version no
    description = db.Column(db.String(80), nullable=True)     # PCO Item Description
    assigned_to = db.Column(db.String(80), nullable=True)     # Name of person(s) assigned to minister
    song_id = db.Column(db.Integer, nullable=True)
    arrangement_id = db.Column(db.Integer, nullable=True)
    arrangement_name = db.Column(db.String(40), nullable=True) # Name of arrangement
    title = db.Column(db.String(40), nullable=False)          # Title of song
    copyright_year = db.Column(db.Integer, nullable=True)
    copyright_holder = db.Column(db.String(40), nullable=True)
    author = db.Column(db.String(40), nullable=True)
    composer = db.Column(db.String(40), nullable=True)
    arranger = db.Column(db.String(40), nullable=True)
    translator = db.Column(db.String(40), nullable=True)      # Text translator
    genre_note = db.Column(db.String(40), nullable=True)
    solo_instruments = db.Column(db.String(80), nullable=True)
    accomp_instruments = db.Column(db.String(80), nullable=True)
    other_performers = db.Column(db.String(256), nullable=True)
    staging_notes = db.Column(db.String(4096), nullable=True)
    song_text = db.Column(db.String(4096), nullable=True)
    copyright_license_status = db.Column(db.Integer, nullable=False, default=COPYRIGHT_STATUS_UNKNOWN)
    start_key = db.Column(db.String(2), nullable=True)  # starting key (ex. Eb)
    end_key = db.Column(db.String(2), nullable=True)    # ending key (ex. F)

    __table_args__ = (db.UniqueConstraint('service_type_id', 'plan_id', 'item_id',  name='_service_plan_item_uc'),
                     )
    
class Person(db.Model):
    USER_TYPE_REGULAR=0
    USER_TYPE_ADMIN=1

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=True)
    email = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    userid = db.Column(db.String(36), nullable=True, unique=True) # Internal userid 
    user_type = db.Column(db.Integer, nullable=False, default=USER_TYPE_REGULAR)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type_id = db.Column(db.Integer, nullable=False)
    plan_id = db.Column(db.Integer, nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_time = db.Column(db.Time, nullable=False)
    theme = db.Column(db.String(80), nullable=True)

    service_items = db.relationship("ServiceItem", back_populates='service')
    __table_args__ = (db.UniqueConstraint('service_type_id', 'plan_id', name='_service_uc'),
                     )
class ServiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id')) # FK to Service
    event = db.Column(db.String(80), nullable=True)
    title = db.Column(db.String(80), nullable=True)
    #song_id = db.Column(db.Integer, nullable=True)
    arrangement_id = db.Column(db.Integer, index=True, nullable=True)
    person_names = db.Column(db.String(80), nullable=True)

    service = db.relationship("Service", back_populates="service_items")
    service_item_people = db.relationship("ServiceItemPerson", back_populates='service_item')

class ServiceItemPerson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_item_id = db.Column(db.Integer, db.ForeignKey('service_item.id')) # FK to ServiceItem
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    person = db.relationship("Person")
    service_item = db.relationship("ServiceItem", back_populates="service_item_people")

class LicensedPublishers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publisher_name = db.Column(db.String(80), nullable=False)

db.create_all() # Create tables from model classes

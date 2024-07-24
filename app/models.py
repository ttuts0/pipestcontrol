from datetime import datetime
from app import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
#                                        'sqlite:///' + os.path.join(basedir, 'app.db')
# db = SQLAlchemy(app)

# Define the Critter model

class Detection(db.Model):
    __tablename__ = 'detection'
    id = db.Column(db.Integer, primary_key=True)
    critter_id = db.Column(db.Integer, db.ForeignKey('critter.id'))
    detection_time = db.Column(db.DateTime, default=datetime.utcnow)
    image_filename = db.Column(db.String(255))  # Ensure image_filename is defined as a column
    
    critter = db.relationship('Critter', back_populates='detections')

class Critter(db.Model):
    __tablename__ = 'critter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    is_pest = db.Column(db.Boolean, default=False)

    detections = db.relationship('Detection', back_populates='critter')

#     @classmethod
#     def delete_by_name(cls, name):
#         critter_to_delete = cls.query.filter_by(name=name).first()
#         if critter_to_delete:
#             db.session.delete(critter_to_delete)
#             db.session.commit()


# def initialize_database():
#     with app.app_context():
#         db.create_all()

#         # Define critters to add or update
#         critters_to_add = [
#             Critter(name='rabbits', is_pest=True),
#             Critter(name='Ladybug', is_pest=False),
#             Critter(name='snail', is_pest=True),
#             Critter(name='grasshopper', is_pest=True),
#             Critter(name='Bee', is_pest=False),
#             Critter(name='butterfly', is_pest=False),



#         ]

#         # Add or update critters in the database
#         for critter in critters_to_add:
#             existing_critter = Critter.query.filter_by(name=critter.name).first()
#             if existing_critter:
#                 existing_critter.is_pest = critter.is_pest
#             else:
#                 db.session.add(critter)
        
#         db.session.commit()

#         # Print all critters in the desired format
        

#         # Example: Remove critter with name 'None'
#         Critter.delete_by_name('cow')

#         critters = Critter.query.all()
#         for critter in critters:
#             print(f"Critter(name='{critter.name}', is_pest={critter.is_pest})")
# # Run the initialization function if script is executed directly
# if __name__ == '__main__':
#     initialize_database()

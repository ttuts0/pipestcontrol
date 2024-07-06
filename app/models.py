from datetime import datetime
from app import db  # Import db from the app package

class Detection(db.Model):
    __tablename__ = 'detection'
    id = db.Column(db.Integer, primary_key=True)
    critter_id = db.Column(db.Integer, db.ForeignKey('critter.id'))
    detection_time = db.Column(db.DateTime, default=datetime)

    critter = db.relationship('Critter', back_populates='detections')

class Critter(db.Model):
    __tablename__ = 'critter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    is_pest = db.Column(db.Boolean, default=False)

    detections = db.relationship('Detection', back_populates='critter')

if __name__ == '__main__':
    from app import app  # Import app to create an app context
    with app.app_context():
        db.create_all()

        # Add test data
        if not Critter.query.first():
            critter1 = Critter(name='Cat', is_pest=False)
            critter2 = Critter(name='Dog', is_pest=False)
            critter3 = Critter(name='Bird', is_pest=True)
            critter4 = Critter(name='Person', is_pest=False)
            critter5 = Critter(name='Bear', is_pest=True)
            critter6 = Critter(name='Elephant', is_pest=True)
            db.session.add_all([critter1, critter2, critter3, critter4, critter5, critter6])
            db.session.commit()

        print("Tables created and test data added")





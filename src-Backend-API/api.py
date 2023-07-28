from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS 

api = Flask(__name__)
api.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:De9654@localhost:5432/backendCheck'
db = SQLAlchemy(api)

# Enable CORS for all routes
CORS(api)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
      return f"Event: {self.description}"
    
    def __init__(self,description):
        self.description = description


def format_event(event):
    return {
        "description": event.description,
        "id": event.id,
        "created_at": event.created_at
    }

@api.route('/')
def hello():
    return 'Hello'

# create an event
@api.route('/event', methods= ['POST'])
def createEvent():
    description = request.json['description']
    event = Event(description)
    db.session.add(event)
    db.session.commit()
    return format_event(event)

# get all events
@api.route('/events', methods= ['GET'])
def getEvents():
    events = Event.query.order_by(Event.id.asc()).all()
    event_list = []
    for event in events:
        event_list.append(format_event(event))
    return {
        'events': event_list
    }

# get single event
@api.route('/events/<id>', methods=['GET'])
def getEvent(id):
    event = Event.query.filter_by(id=id).one()
    formated_event = format_event(event)
    return {
        "event": formated_event
    }

if __name__ == '__main__':
    with api.app_context():  # Set up the application context
        db.create_all()      # Create the database tables
    api.run()
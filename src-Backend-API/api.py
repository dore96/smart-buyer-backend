from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

api = Flask(__name__)
api.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:De9654@localhost:5432/backendCheck'
db = SQLAlchemy(api)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
      return f"Event: {self.description}"
    
    def __init__(self,description):
        self.description = description

@api.route('/')
def hello():
    print("Inside the 'hello' route")  # Add this line for debugging
    return 'Hello'

if __name__ == '__main__':
    api.run()
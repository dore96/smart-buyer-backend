from app import create_app
from app.models import db
import sys
import os

# Get the current directory of the 'run.py' script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (the root of the project) and add it to sys.path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        db.create_all()

    app.run()
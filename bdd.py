from flask import Flask
from db_connection import db  # Adjust the import to match your project structure

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://adrien:password@localhost/perso'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Use the application context
with app.app_context():
    db.create_all()
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Calcul(db.Model):
    __tablename__ = 'calcul'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Integer)
    somme = db.Column(db.Integer)
    utilisateur = db.Column(db.String)
    date_calcul = db.Column(db.DateTime)

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    nb_test = db.Column(db.Integer)
    date_upload = db.Column(db.DateTime)
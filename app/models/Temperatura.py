from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.extensions import db


class Temperatura(db.Model):
    __tablename__ = 'temperaturas'

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

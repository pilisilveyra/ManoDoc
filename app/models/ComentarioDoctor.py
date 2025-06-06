from datetime import datetime

from app.extensions import db

class ComentarioDoctor(db.Model):
    __tablename__ = 'ComentarioDoctor'
    id_comentario = db.Column(db.Integer, primary_key=True)
    id_operacion = db.Column(db.Integer, db.ForeignKey('operaciones.id_operacion'), nullable=False)
    contenido = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
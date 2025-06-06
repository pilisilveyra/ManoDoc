from datetime import datetime
from app.extensions import db

class Operacion(db.Model):
    __tablename__ = 'operaciones'

    id_operacion = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(50), nullable=False, default='en_curso')  # en_curso, pausa, finalizada
    tipo = db.Column(db.String(100), nullable=False)
    inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fin = db.Column(db.DateTime)

    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_doctor = db.Column(db.Integer, db.ForeignKey('doctor.id_doctor'), nullable=False)

    paciente = db.relationship('Paciente', backref=db.backref('operaciones', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('operaciones', lazy=True))
from app.extensions import db
from datetime import date, time

class Turno(db.Model):
    __tablename__ = 'turnos'

    id_turno = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)

    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_doctor = db.Column(db.Integer, db.ForeignKey('doctor.id_doctor'), nullable=False)
    tipo_operacion = db.Column(db.String(100), nullable=False)

    doctor_ingreso = db.Column(db.Boolean, default=False)
    paciente_ingreso = db.Column(db.Boolean, default=False)

    # Relaciones (opcionales pero útiles)
    paciente = db.relationship('Paciente', backref=db.backref('turnos', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('turnos', lazy=True))


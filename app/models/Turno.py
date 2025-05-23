from app.extensions import db
from datetime import date, time

class Turno(db.Model):
    __tablename__ = 'turnos'

    id_turno = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)

    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id_paciente'), nullable=False)
    id_doctor = db.Column(db.Integer, db.ForeignKey('doctores.id_doctor'), nullable=False)

    # Relaciones (opcionales pero útiles)
    paciente = db.relationship('Paciente', backref=db.backref('turnos', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('turnos', lazy=True))

    def __repr__(self):
        return f"<Turno {self.fecha} {self.hora} - Paciente {self.id_paciente} - Doctor {self.id_doctor}>"

from app.extensions import db

class Paciente(db.Model):
    __tablename__ = 'paciente'

    id_paciente = db.Column(db.Integer, primary_key=True)

from app.extensions import db

class Paciente(db.Model):
    __tablename__ = 'paciente'

    id_paciente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(256), nullable=False)
    dni = db.Column(db.String(8), unique=True, nullable=False)



from flask import Blueprint, request, redirect, url_for, render_template
from app.extensions import db
from app.models.Paciente import Paciente
from app.models.Doctor import Doctor
from werkzeug.security import generate_password_hash

register_bp = Blueprint('register_bp', __name__)

@register_bp.route('/register')
def register():
    return render_template('register.html')

@register_bp.route('/registrar_paciente', methods=['POST'])
def registrar_paciente():
    hashed_password = generate_password_hash(request.form['contrasena'])

    nuevo = Paciente(
        nombre=request.form['nombre'],
        apellido=request.form['apellido'],
        email=request.form['email'],
        contrasena=hashed_password,
        dni=request.form['dni']
    )

    db.session.add(nuevo)
    db.session.commit()
    return render_template("home-paciente.html")

@register_bp.route('/registrar_doctor', methods=['POST'])
def registrar_doctor():
    hashed_password = generate_password_hash(request.form['contrasena'])
    nuevo = Doctor(
        nombre=request.form['nombre'],
        apellido=request.form['apellido'],
        email=request.form['email'],
        contrasena=hashed_password,
        dni=request.form['dni'],
        especialidad=request.form['especialidad'],
        foto=request.form['foto']
    )
    db.session.add(nuevo)
    db.session.commit()
    return render_template("home-doctor.html")

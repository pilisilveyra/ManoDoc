from flask import Blueprint, request, redirect, url_for, render_template
from app.extensions import db
from app.models.Paciente import Paciente
from app.models.Doctor import Doctor
from werkzeug.security import generate_password_hash
from flask import flash

register_bp = Blueprint('register_bp', __name__)

@register_bp.route('/register')
def register():
    return render_template('register.html')

@register_bp.route('/registrar_paciente', methods=['POST'])
def registrar_paciente():
    email = request.form['email']
    dni = request.form['dni']

    if Paciente.query.filter_by(email=email).first() or Doctor.query.filter_by(email=email).first():
        flash("Ya existe una cuenta registrada con ese email.")
        return render_template('register.html')

    if Paciente.query.filter_by(dni=dni).first() or Doctor.query.filter_by(dni=dni).first():
        flash("Ya existe una cuenta registrada con ese DNI.")
        return render_template('register.html')

    hashed_password = generate_password_hash(request.form['contrasena'])

    nuevo = Paciente(
        nombre=request.form['nombre'],
        apellido=request.form['apellido'],
        telefono=request.form['telefono'],
        email=email,
        contrasena=hashed_password,
        dni=dni,
        cobertura=request.form['cobertura'],
        foto=request.form['foto']
    )

    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for('index'))

@register_bp.route('/registrar_doctor', methods=['POST'])
def registrar_doctor():
    email = request.form['email']
    dni = request.form['dni']

    if Paciente.query.filter_by(email=email).first() or Doctor.query.filter_by(email=email).first():
        flash("Ya existe una cuenta registrada con ese email.")
        return render_template('register.html')

    if Paciente.query.filter_by(dni=dni).first() or Doctor.query.filter_by(dni=dni).first():
        flash("Ya existe una cuenta registrada con ese DNI.")
        return render_template('register.html')

    hashed_password = generate_password_hash(request.form['contrasena'])

    nuevo = Doctor(
        nombre=request.form['nombre'],
        apellido=request.form['apellido'],
        email=email,
        contrasena=hashed_password,
        dni=dni,
        especialidad=request.form['especialidad'],
        foto=request.form['foto']
    )

    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for('index'))

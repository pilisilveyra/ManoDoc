from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models.Paciente import Paciente
from app.models.Doctor import Doctor
from werkzeug.security import check_password_hash
login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']

        # Buscar en Pacientes
        paciente = Paciente.query.filter_by(email=email).first()
        if paciente and check_password_hash(paciente.contrasena, contrasena):
            session['usuario_id'] = paciente.id_paciente
            session['tipo'] = 'paciente'
            return redirect(url_for('home'))  # o redirigir a panel de paciente

        # Buscar en Doctores
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor and check_password_hash(doctor.contrasena, contrasena):
            session['usuario_id'] = doctor.id_doctor
            session['tipo'] = 'doctor'
            return redirect(url_for('home'))  # o redirigir a panel de doctor

        flash('Email o contraseña incorrectos')
        return redirect(url_for('login_bp.login'))

    return render_template('login.html')


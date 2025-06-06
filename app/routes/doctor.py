from datetime import date

from flask import Blueprint, request, redirect, url_for, render_template, session, flash, jsonify

from app import db
from app.models.Doctor import Doctor
from app.models.Paciente import Paciente
from app.models.Turno import Turno

doctor_bp = Blueprint('doctor_bp', __name__, template_folder='templates')

@doctor_bp.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([
        {
            'id': doctor.id_doctor,
            'nombre': doctor.nombre,
            'apellido': doctor.apellido,
            'especialidad': doctor.especialidad,
            'imagen_url': doctor.foto
        }
        for doctor in doctors
    ])

@doctor_bp.route('/turnos-doctor')
def turnos_doctor():
    if 'usuario_id' in session and session.get('tipo') == 'doctor':
        id_doctor = session['usuario_id']
        from datetime import datetime
        turnos = Turno.query.filter(
            Turno.id_doctor == id_doctor,
            db.func.concat(Turno.fecha, ' ', Turno.hora) >= datetime.now()
        ).all()
        # Filtrá los que NO tienen operación o tienen operación que no finalizó
        turnos = [t for t in turnos if not t.operacion or t.operacion.estado != 'finalizada']
        return render_template('turnos-doctor.html', turnos=turnos, active_page='turnos')
    return redirect(url_for('login_bp.login'))

@doctor_bp.route('/turnos/<int:id_turno>/cancelar', methods=['POST'])
def cancelar_turno_doctor(id_turno):
    turno = Turno.query.get_or_404(id_turno)
    db.session.delete(turno)
    db.session.commit()
    return redirect(url_for('doctor_bp.turnos_doctor'))


@doctor_bp.route('/historial-operaciones')
def historial_operaciones():
    return render_template('historial-operaciones-doctor.html', active_page='historial')

@doctor_bp.route('/perfil-doctor')
def perfil_doctor():
    if 'usuario_id' in session and session.get('tipo') == 'doctor':
        doctor = Doctor.query.get(session['usuario_id'])
        return render_template('perfil-doctor.html', doctor=doctor, active_page='perfil')
    return redirect(url_for('login_bp.login'))

@doctor_bp.route('/turnos/<int:id_turno>/ingresar')
def ingresar_turno_doctor(id_turno):
    session['turno_en_curso'] = id_turno
    session['tipo'] = 'doctor'
    return redirect(url_for('ver_cita'))
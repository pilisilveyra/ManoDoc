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
        ahora = datetime.now()
        turnos = Turno.query.filter_by(id_doctor=id_doctor).all()

        turnos_futuros = [
            t for t in turnos
            if datetime.combine(t.fecha, t.hora) >= ahora
               and (not t.operacion or t.operacion.estado != 'finalizada')
        ]
        return render_template('turnos-doctor.html', turnos=turnos_futuros, active_page='turnos')
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
    turno = Turno.query.get_or_404(id_turno)
    turno.doctor_ingreso = True
    db.session.commit()
    session['turno_en_curso'] = id_turno
    print(session.get('tipo'))
    return redirect(url_for('ver_cita'))

from flask import request, jsonify
from app.models.ComentarioDoctor import ComentarioDoctor
from app.models.Operacion import Operacion
from app.extensions import db
from datetime import datetime

from flask import redirect, url_for

@doctor_bp.route('/comentarios', methods=['POST'])
def guardar_comentario():
    if 'usuario_id' not in session or session.get('tipo') != 'doctor':
        return redirect(url_for('login_bp.login'))

    id_operacion = request.form.get('id_operacion', type=int)
    contenido = request.form.get('comentario', type=str)

    if not id_operacion or not contenido:
        flash("Faltan datos para guardar el comentario")
        return redirect(url_for('ver_cita'))

    comentario = ComentarioDoctor(
        id_operacion=id_operacion,
        contenido=contenido,
    )
    db.session.add(comentario)
    db.session.commit()

    return redirect(url_for('ver_cita'))

@doctor_bp.route('/finalizar-operacion', methods=['POST'])
def finalizar_operacion():
    op_id = request.form.get('id_operacion')
    operacion = Operacion.query.get_or_404(op_id)
    operacion.estado = 'finalizada'
    db.session.commit()
    return redirect(url_for('ver_cita'))


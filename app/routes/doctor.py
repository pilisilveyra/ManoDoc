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
        ).order_by(Turno.fecha, Turno.hora).all()
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
    turno = Turno.query.get_or_404(id_turno)
    turno.doctor_ingreso = True
    db.session.commit()
    session['turno_en_curso'] = id_turno
    return redirect(url_for('ver_cita_doctor'))

@doctor_bp.route('/ver-cita', methods=['GET', 'POST'])
def ver_cita_doctor():
    from app.models.Turno import Turno
    from app.models.Operacion import Operacion
    from app.models.ComentarioDoctor import ComentarioDoctor
    from app.models.Temperatura import Temperatura
    from app.extensions import db

    turno_id = session.get('turno_en_curso')
    if not turno_id:
        return redirect(url_for('index'))

    turno = Turno.query.get_or_404(turno_id)

    tipo = session.get('tipo')
    if tipo == 'doctor' and not turno.doctor_ingreso:
        turno.doctor_ingreso = True
        db.session.commit()


    if not (turno.doctor_ingreso and turno.paciente_ingreso):
        return render_template('ver_cita_esperando.html')

    operacion = Operacion.query.filter_by(
        id_paciente=turno.id_paciente,
        id_doctor=turno.id_doctor,
        estado='en_curso'
    ).first()

    if not operacion:
        operacion = Operacion(
            tipo=turno.tipo_operacion,
            id_paciente=turno.id_paciente,
            id_doctor=turno.id_doctor
        )
        db.session.add(operacion)
        db.session.commit()

    # Si envió un comentario
    if request.method == 'POST':
        contenido = request.form.get("comentario")
        if contenido:
            nuevo = ComentarioDoctor(
                contenido=contenido,
                id_operacion=operacion.id_operacion
            )
            db.session.add(nuevo)
            db.session.commit()

    return render_template("ver_cita_doctor.html", operacion=operacion, paciente=turno.paciente)







from datetime import date, datetime

from flask import Blueprint, request, redirect, url_for, render_template, session, flash

from app import db
from app.models.Paciente import Paciente
from app.models.Turno import Turno
from app.models.Doctor import Doctor

paciente_bp = Blueprint('paciente_bp', __name__, template_folder='templates')

@paciente_bp.route('/home-paciente')
def home_paciente():
    if 'usuario_id' in session and session['tipo'] == 'paciente':
        paciente = Paciente.query.get(session['usuario_id'])
        turnos = Turno.query.filter_by(id_paciente=paciente.id_paciente).filter(Turno.fecha >= date.today()).all()
        return render_template('home-paciente.html', paciente=paciente, turnos=turnos, active_page='home')
    else:
        return render_template('login.html')


@paciente_bp.route('/historial-paciente')
def historial_paciente():
    return render_template('historial-paciente.html')

from datetime import datetime, date, time

@paciente_bp.route('/turnos-paciente')
def turnos_paciente():
    if 'usuario_id' in session and session['tipo'] == 'paciente':
        paciente = Paciente.query.get(session['usuario_id'])

        ahora = datetime.now()

        # Traer todos los turnos del paciente
        turnos = Turno.query.filter_by(id_paciente=paciente.id_paciente).all()

        # Filtrar solo los futuros (fecha y hora juntos)
        turnos_futuros = [
            turno for turno in turnos
            if datetime.combine(turno.fecha, turno.hora) >= ahora
        ]

        doctores = Doctor.query.all()

        return render_template('turnos-paciente.html',
                               paciente=paciente,
                               turnos=turnos_futuros,
                               doctores=doctores,
                               active_page='turnos')
    return redirect(url_for('login_bp.login'))

@paciente_bp.route('/perfil-paciente')
def perfil_paciente():
    if 'usuario_id' in session and session.get('tipo') == 'paciente':
        paciente = Paciente.query.get(session['usuario_id'])
        return render_template('perfil-paciente.html', paciente=paciente, active_page='perfil')
    return redirect(url_for('login_bp.login'))

@paciente_bp.route('/nuevo-turno')
def nuevo_turno():
    if 'usuario_id' in session and session['tipo'] == 'paciente':
        doctores = Doctor.query.all()
        return render_template('nuevo-turno.html', doctores=doctores, active_page='turnos')
    return redirect(url_for('login_bp.login'))

@paciente_bp.route('/crear-turno', methods=['POST'])
def crear_turno():
    if 'usuario_id' in session and session['tipo'] == 'paciente':
        id_paciente = session['usuario_id']
        id_doctor = request.form['id_doctor']
        fecha = request.form['fecha']
        hora = request.form['hora']
        tipo_operacion = request.form['tipo_operacion']

        turno = Turno(
            id_paciente=id_paciente,
            id_doctor=id_doctor,
            fecha=datetime.strptime(fecha, "%Y-%m-%d").date(),
            hora=datetime.strptime(hora, "%H:%M").time(),
            tipo_operacion = tipo_operacion
        )
        db.session.add(turno)
        db.session.commit()

        return redirect(url_for('paciente_bp.turnos_paciente'))
    return redirect(url_for('login_bp.login'))

@paciente_bp.route('/cancelar-turno/<int:id_turno>', methods=['POST'])
def cancelar_turno(id_turno):
    turno = Turno.query.get(id_turno)
    db.session.delete(turno)
    db.session.commit()
    return redirect(url_for('paciente_bp.turnos_paciente'))

@paciente_bp.route('/turnos/<int:id_turno>/ingresar')
def ingresar_turno_paciente(id_turno):
    turno = Turno.query.get_or_404(id_turno)
    turno.paciente_ingreso = True
    db.session.commit()
    session['turno_en_curso'] = id_turno
    return redirect(url_for('paciente_bp.ver_cita_paciente'))

@paciente_bp.route('/ver-cita')
def ver_cita_paciente():
    from app.models.Turno import Turno
    from app.models.Operacion import Operacion
    from app.models.ComentarioDoctor import ComentarioDoctor

    turno_id = session.get('turno_en_curso')
    if not turno_id:
        return redirect(url_for('index'))

    turno = Turno.query.get_or_404(turno_id)

    tipo = session.get('tipo')
    if tipo == 'paciente' and not turno.paciente_ingreso:
        turno.paciente_ingreso = True
        db.session.commit()

    if not (turno.doctor_ingreso and turno.paciente_ingreso):
        return render_template('ver_cita_esperando.html')

    operacion = Operacion.query.filter_by(
        id_turno=turno.id_turno,
        estado='en_curso'
    ).first()

    if not operacion:
        return render_template('ver_cita_esperando.html')  # Fallback seguro

    comentarios = ComentarioDoctor.query.filter_by(id_operacion=operacion.id_operacion).order_by(ComentarioDoctor.timestamp.desc()).all()

    return render_template("ver_cita_paciente.html", operacion=operacion, doctor=turno.doctor, comentarios=comentarios)

@paciente_bp.route('/comentarios')
def obtener_comentarios():
    id_operacion = request.args.get("id_operacion", type=int)
    comentarios = ComentarioDoctor.query.filter_by(id_operacion=id_operacion).order_by(ComentarioDoctor.timestamp.desc()).all()
    operacion = Operacion.query.get_or_404(id_operacion)

    return jsonify([
        {
            "contenido": c.contenido,
            "timestamp": c.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "estado_operacion": operacion.estado  # Se repite en todos para fácil lectura
        }
        for c in comentarios
    ])

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

        turno = Turno(
            id_paciente=id_paciente,
            id_doctor=id_doctor,
            fecha=datetime.strptime(fecha, "%Y-%m-%d").date(),
            hora=datetime.strptime(hora, "%H:%M").time()
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
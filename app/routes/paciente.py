from datetime import date

from flask import Blueprint, request, redirect, url_for, render_template, session, flash

from app.models.Paciente import Paciente
from app.models.Turno import Turno

paciente_bp = Blueprint('paciente_bp', __name__, template_folder='templates')

@paciente_bp.route('/home-paciente')
def home_paciente():
    if 'usuario_id' in session and session['tipo'] == 'paciente':
        paciente = Paciente.query.get(session['usuario_id'])
        turnos = Turno.query.filter_by(paciente_id=paciente.id).filter(Turno.fecha >= date.today()).all()
        return render_template('home-paciente.html', turnos=turnos)
    else:
        return render_template('login.html')


@paciente_bp.route('/historial-paciente')
def historial_paciente():
    return render_template('historial-paciente.html')

@paciente_bp.route('/turnos-paciente')
def turnos_paciente():
    return render_template('turnos-paciente.html')

@paciente_bp.route('/perfil-paciente')
def perfil_paciente():
    return render_template('perfil-paciente.html')




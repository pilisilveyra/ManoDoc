import pymysql

pymysql.install_as_MySQLdb()

from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from app.extensions import db
from app.routes.register import register_bp
from app.routes.login import login_bp
from app.routes.paciente import paciente_bp
from app.routes.doctor import doctor_bp
from app.routes.temperaturas import temperaturas_bp
import os

def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get('SECRET_KEY', 'clave-secreta-default')

    app.config.from_object('app.config')

    db.init_app(app)

    with app.app_context():
        from app.models.Doctor import Doctor
        from app.models.Paciente import Paciente
        from app.models.Turno import Turno
        from app.models.Temperatura import Temperatura
        from app.models.Operacion import Operacion
        from app.models.ComentarioDoctor import ComentarioDoctor
        db.create_all()

    app.register_blueprint(register_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(paciente_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(temperaturas_bp)

    @app.context_processor
    def inject_paciente():
        if 'usuario_id' in session and session.get('tipo') == 'paciente':
            paciente = Paciente.query.get(session['usuario_id'])
            return dict(paciente=paciente)
        return {}

    @app.context_processor
    def inject_doctor():
        if 'usuario_id' in session and session.get('tipo') == 'doctor':
            doctor = Doctor.query.get(session['usuario_id'])
            return dict(doctor=doctor)
        return {}


    @app.route('/')
    def index():
        return render_template('login.html')


    import paho.mqtt.publish as publish


    @app.route('/ver-cita/estado')
    def ver_cita_estado():
        turno_id = session.get('turno_en_curso')
        tipo = session.get('tipo')
        if not turno_id or tipo not in ['doctor', 'paciente']:
            return jsonify({"en_curso": False})

        turno = Turno.query.get(turno_id)
        db.session.refresh(turno)
        puede_ingresar = turno.doctor_ingreso and turno.paciente_ingreso

        redireccion = "/ver-cita"
        if tipo == "doctor":
            redireccion = url_for("doctor_bp.ver_cita_doctor")
        elif tipo == "paciente":
            redireccion = url_for("paciente_bp.ver_cita_paciente")

        return jsonify({"en_curso": puede_ingresar, "url": redireccion})

    @app.route('/iniciar-mano')
    def iniciar_mano():
        publish.single("start/hand", payload="start", hostname="52.21.40.175")
        return "OK"

    @app.route('/mano')
    def mano():
        return render_template('mano.html')

    return app


import pymysql

pymysql.install_as_MySQLdb()

from flask import Flask, render_template, redirect, url_for, session, jsonify
from app.extensions import db
from app.routes.register import register_bp
from app.routes.login import login_bp
from app.routes.paciente import paciente_bp
from app.routes.doctor import doctor_bp
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
        db.create_all()

    app.register_blueprint(register_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(paciente_bp)
    app.register_blueprint(doctor_bp)

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

    @app.route('/temperaturas')
    def temperaturas():
        from app.models.Temperatura import Temperatura
        datos = Temperatura.query.order_by(Temperatura.timestamp.desc()).limit(20).all()
        return render_template('temperaturas.html', temperaturas=datos)

    @app.route('/temperaturas/datos')
    def temperaturas_datos():
        from app.models.Temperatura import Temperatura
        datos = Temperatura.query.order_by(Temperatura.timestamp.desc()).limit(20).all()
        return jsonify([
            {
                "valor": t.valor,
                "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "id_operacion": t.id_operacion
            }
            for t in datos
        ])

    import paho.mqtt.publish as publish

    @app.route('/ver-cita')
    def ver_cita():
        turno_id_doc = session.get('doctor_ingreso_turno')
        turno_id_pac = session.get('paciente_ingreso_turno')

        if turno_id_doc and turno_id_pac and turno_id_doc == turno_id_pac:
            turno = Turno.query.get(turno_id_doc)

            # Si no hay operación activa, crearla
            from app.models.Operacion import Operacion
            op = Operacion.query.filter_by(
                id_paciente=turno.id_paciente,
                id_doctor=turno.id_doctor,
                estado="en_curso"
            ).first()

            if not op:
                op = Operacion(
                    tipo=turno.tipo_operacion,
                    id_paciente=turno.id_paciente,
                    id_doctor=turno.id_doctor
                )
                db.session.add(op)
                db.session.commit()

            return render_template('ver_cita.html', operacion=op)

        # Si aún falta alguien, mostramos mensaje de espera
        return render_template('ver_cita_esperando.html')

    @app.route('/ver-cita/estado')
    def estado_cita():
        turno_id_doc = session.get('doctor_ingreso_turno')
        turno_id_pac = session.get('paciente_ingreso_turno')

        if turno_id_doc and turno_id_pac and turno_id_doc == turno_id_pac:
            return {"en_curso": True}
        return {"en_curso": False}

    @app.route('/iniciar-mano')
    def iniciar_mano():
        publish.single("start/hand", payload="start", hostname="52.21.40.175")
        return "OK"

    @app.route('/mano')
    def mano():
        return render_template('mano.html')

    return app


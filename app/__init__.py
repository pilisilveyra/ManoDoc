import pymysql
from datetime import timedelta

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
    app.permanent_session_lifetime = timedelta(minutes=30)

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
        if 'usuario_id' in session:
            if session.get('tipo') == 'paciente':
                return redirect(url_for('paciente_bp.home_paciente'))
            elif session.get('tipo') == 'doctor':
                return redirect(url_for('doctor_bp.turnos_doctor'))
        return render_template('login.html')

    import paho.mqtt.publish as publish
    @app.route('/ver-cita')
    def ver_cita():
        turno_id = session.get('turno_en_curso')
        if not turno_id:
            return redirect(url_for('index'))

        db.session.expire_all()
        turno = db.session.query(Turno).filter_by(id_turno=turno_id).first()

        tipo = session.get('tipo')


        if turno.doctor_ingreso and turno.paciente_ingreso:
            op = Operacion.query.filter_by(id_turno=turno.id_turno).first()

            if not op:
                op = Operacion(
                    tipo=turno.tipo_operacion,
                    id_paciente=turno.id_paciente,
                    id_doctor=turno.id_doctor,
                    id_turno=turno.id_turno
                )
                db.session.add(op)
                db.session.commit()

            if op.estado == 'finalizada':
                return render_template("ver_cita_finalizada.html")  # página con el mensaje y botón para salir

            if tipo == 'doctor':
                return render_template("ver_cita_doctor.html", operacion=op, paciente=turno.paciente)
            else:
                comentarios = ComentarioDoctor.query.filter_by(
                    id_operacion=op.id_operacion
                ).order_by(ComentarioDoctor.timestamp.desc()).all()
                return render_template("ver_cita_paciente.html", operacion=op, doctor=turno.doctor,
                                       comentarios=comentarios)

        return render_template('ver_cita_esperando.html')

    @app.route('/ver-cita/estado')
    def estado_cita():
        turno_id = session.get('turno_en_curso')
        if not turno_id:
            return {"en_curso": False}

        from app.models.Turno import Turno
        db.session.expire_all()
        turno = db.session.query(Turno).filter_by(id_turno=turno_id).first()


        return {"en_curso": bool(turno and turno.paciente_ingreso and turno.doctor_ingreso)}


    @app.route('/iniciar-mano')
    def iniciar_mano():
        publish.single("start/hand", payload="start", hostname="52.21.40.175")
        return "OK"

    @app.route('/mano')
    def mano():
        return render_template('mano.html')

    @app.route('/operacion/<int:id_operacion>/estado-actual')
    def obtener_estado_operacion(id_operacion):
        operacion = Operacion.query.get_or_404(id_operacion)
        return jsonify({"estado": operacion.estado})

    return app


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
    @app.route('/ver-cita', methods=['GET', 'POST'])
    def ver_cita():
        from app.models.Turno import Turno
        from app.models.Operacion import Operacion
        from app.models.ComentarioDoctor import ComentarioDoctor
        from app.extensions import db

        turno_id = session.get('turno_en_curso')
        tipo = session.get('tipo')

        if not turno_id or tipo not in ['doctor', 'paciente']:
            return redirect(url_for('index'))

        turno = Turno.query.get_or_404(turno_id)
        db.session.refresh(turno)

        # ✅ Marcar el ingreso según el tipo
        if tipo == 'paciente' and not turno.paciente_ingreso:
            turno.paciente_ingreso = True
            db.session.commit()
        elif tipo == 'doctor' and not turno.doctor_ingreso:
            turno.doctor_ingreso = True
            db.session.commit()

        # ⏳ Si alguno todavía no ingresó, esperar
        if not (turno.paciente_ingreso and turno.doctor_ingreso):
            return render_template("ver_cita_esperando.html")

        # 🏥 Crear la operación si no existe
        operacion = Operacion.query.filter_by(
            id_turno=turno.id_turno,
            estado='en_curso'
        ).first()

        if not operacion:
            operacion = Operacion(
                tipo=turno.tipo_operacion,
                id_paciente=turno.id_paciente,
                id_doctor=turno.id_doctor,
                id_turno=turno.id_turno
            )
            db.session.add(operacion)
            db.session.commit()

        # 📝 Comentario del doctor
        if request.method == 'POST':
            if tipo == 'doctor':
                if "comentario" in request.form:
                    contenido = request.form.get("comentario")
                    if contenido:
                        nuevo = ComentarioDoctor(
                            contenido=contenido,
                            id_operacion=operacion.id_operacion
                        )
                        db.session.add(nuevo)
                        db.session.commit()

                elif "nuevo_estado" in request.form:
                    nuevo_estado = request.form.get("nuevo_estado")
                    if nuevo_estado in ['en_curso', 'en_pausa', 'finalizada']:
                        operacion.estado = nuevo_estado
                        db.session.commit()
                        if nuevo_estado == 'finalizada':
                            session.pop("turno_en_curso", None)
                            return redirect(url_for('doctor_bp.turnos_doctor'))

        # 👨‍⚕️ Renderizar según tipo
        if tipo == 'doctor':
            return render_template("ver_cita_doctor.html", operacion=operacion, paciente=turno.paciente)
        else:
            comentarios = ComentarioDoctor.query.filter_by(
                id_operacion=operacion.id_operacion
            ).order_by(ComentarioDoctor.timestamp.desc()).all()
            return render_template("ver_cita_paciente.html", operacion=operacion, doctor=turno.doctor,
                                   comentarios=comentarios)

    @app.route('/ver-cita/estado')
    def ver_estado_cita():
        turno_id = session.get('turno_en_curso')
        tipo = session.get('tipo')

        if not turno_id or tipo not in ['doctor', 'paciente']:
            return jsonify({"en_curso": False})

        turno = Turno.query.get(turno_id)

        # Forzamos refresco desde la DB
        db.session.refresh(turno)

        if turno.doctor_ingreso and turno.paciente_ingreso:
            return jsonify({"en_curso": True, "url": url_for("ver_cita")})

        return jsonify({"en_curso": False})

    @app.route('/iniciar-mano')
    def iniciar_mano():
        publish.single("start/hand", payload="start", hostname="52.21.40.175")
        return "OK"

    @app.route('/mano')
    def mano():
        return render_template('mano.html')

    return app


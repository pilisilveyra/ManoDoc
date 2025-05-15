import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config')

    db.init_app(app)

    with app.app_context():
        from app.models.Temperatura import Temperatura
        from app.models.Paciente import Paciente
        from app.models.Doctor import Doctor
        db.create_all()


    @app.route('/')
    def home():
        return render_template('home.html', active_page='home')

    @app.route('/turnos')
    def turnos():
        return render_template('turnos.html', active_page='turnos')

    @app.route('/historial')
    def historial():
        return render_template('historial.html', active_page='historial')

    @app.route('/perfil')
    def perfil():
        return render_template('perfil.html', active_page='perfil')

    @app.route('/contact')
    def contact():
        return render_template('contact.html', active_page='contact')

    @app.route('/temperaturas')
    def temperaturas():
        from app.models.Temperatura import Temperatura
        datos = Temperatura.query.order_by(Temperatura.timestamp.desc()).limit(20).all()
        return render_template('temperaturas.html', temperaturas=datos)

    return app

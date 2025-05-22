import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template
from app.extensions import db
from app.routes.register import register_bp
from app.routes.login import login_bp
import os

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    app.config.from_object('app.config')

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(register_bp)
    app.register_blueprint(login_bp)

    @app.route('/')
    def login_view():
        return render_template('login.html')

    @app.route('/register')
    def register_view():
        return render_template('register.html')

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

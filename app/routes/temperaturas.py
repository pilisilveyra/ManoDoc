from flask import Blueprint, render_template, request, jsonify

temperaturas_bp = Blueprint('temperaturas_bp', __name__, template_folder='templates')

@temperaturas_bp.route('/temperaturas')
def temperaturas():
    from app.models.Temperatura import Temperatura
    datos = Temperatura.query.order_by(Temperatura.timestamp.desc()).limit(20).all()
    return render_template('temperaturas.html', temperaturas=datos)

@temperaturas_bp.route('/temperaturas/datos')
def temperaturas_datos():
    from app.models.Temperatura import Temperatura

    id_operacion = request.args.get('id_operacion', type=int)

    query = Temperatura.query.order_by(Temperatura.timestamp.desc())
    if id_operacion:
        query = query.filter_by(id_operacion=id_operacion)

    datos = query.limit(20).all()
    return jsonify([
        {
            "valor": t.valor,
            "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "id_operacion": t.id_operacion
        }
        for t in datos
    ])
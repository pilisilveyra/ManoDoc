import paho.mqtt.client as mqtt
from app import create_app
from app.extensions import db
from app.models.Temperatura import Temperatura

app = create_app()

MQTT_BROKER = "52.21.40.175"
TOPIC = "temperatura"

def on_connect(client, userdata, flags, rc):
    print("Conectado con código", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        valor = float(msg.payload.decode())
        with app.app_context():
            from app.models.Operacion import Operacion
            operacion_activa = Operacion.query.filter_by(estado='en_curso').first()

            if operacion_activa:
                nueva = Temperatura(valor=valor, id_operacion=operacion_activa.id_operacion)
                db.session.add(nueva)
                db.session.commit()
                print(f"Temperatura guardada: {valor} asociada a operación {operacion_activa.id_operacion}")
            else:
                print("No hay operación en curso. No se guardó la temperatura.")
    except Exception as e:
        print("Error al guardar:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()

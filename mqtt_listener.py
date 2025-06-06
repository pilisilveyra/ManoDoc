import paho.mqtt.client as mqtt
from app import create_app
from app.extensions import db
from app.models.Temperatura import Temperatura

app = create_app()

MQTT_BROKER = "52.21.40.175"
TOPIC = "temperatura"

def on_connect(client, userdata, flags, rc):
    print("Conectado con código", rc)
    if rc == 0:
        client.subscribe(TOPIC)
        print(f"Suscrito a {TOPIC}")

def on_message(client, userdata, msg):
    print(f"¡MENSAJE RECIBIDO! Topic: {msg.topic}, Payload: {msg.payload.decode()}")
    try:
        valor = float(msg.payload.decode())
        with app.app_context():
            # Simplificado: guardar sin operación por ahora
            nueva = Temperatura(valor=valor)
            db.session.add(nueva)
            db.session.commit()
        print("Temperatura guardada:", valor)
    except Exception as e:
        print("Error al guardar:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Conectando al broker...")
client.connect(MQTT_BROKER, 1883, 60)
print("Iniciando loop...")
client.loop_forever()
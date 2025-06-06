import threading
from app import create_app
from app.extensions import db
from app.models.Temperatura import Temperatura
import paho.mqtt.client as mqtt

app = create_app()

# --- Configuración MQTT ---
MQTT_BROKER = "52.21.40.175"
TOPIC = "temperatura"

def on_connect(client, userdata, flags, rc):
    print("MQTT conectado con código", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        valor = float(msg.payload.decode())
        with app.app_context():
            nueva = Temperatura(valor=valor)
            db.session.add(nueva)
            db.session.commit()
        print("Temperatura guardada:", valor)
    except Exception as e:
        print("Error al guardar temperatura:", e)

def iniciar_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()

# --- Inicio de todo ---
if __name__ == "__main__":
    # Lanzar hilo para MQTT
    mqtt_thread = threading.Thread(target=iniciar_mqtt)
    mqtt_thread.daemon = True  # se cierra cuando el main termina
    mqtt_thread.start()

    # Iniciar Flask
    app.run(host='0.0.0.0', debug=True)

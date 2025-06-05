import cv2
import paho.mqtt.client as mqtt
from cvzone.HandTrackingModule import HandDetector

BROKER = "52.21.40.175"

PORT = 1883
TOPIC_CONTROL = "start/hand"
TOPIC_RESULTADO = "mano/dedos"

def on_message(client, userdata, message):
    print("🟢 Recibida orden de iniciar mano")
    detectar_mano()

def detectar_mano():
    client_pub = mqtt.Client()
    client_pub.connect(BROKER, PORT, 60)

    cap = cv2.VideoCapture(0)
    detector = HandDetector(maxHands=1, detectionCon=0.7)

    while True:
        success, img = cap.read()
        if not success:
            break

        hands, bbox = detector.findHands(img)
        if hands:
            fingers = detector.fingersUp(hands[0])
            mensaje = f"${''.join(map(str, fingers))}"
            print(f"✋ Enviando: {mensaje}")
            client_pub.publish(TOPIC_RESULTADO, mensaje)

        cv2.imshow("Detección de Mano", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    client_pub.disconnect()

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC_CONTROL)
print("🟡 Esperando orden para iniciar detección de mano...")
client.loop_forever()

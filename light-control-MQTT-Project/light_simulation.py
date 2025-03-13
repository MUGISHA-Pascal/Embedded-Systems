import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
TOPIC = "/student_group/light_control"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    command = msg.payload.decode()
    if command == "ON":
        print("💡 Light is TURNED ON")
    elif command == "OFF":
        print("💡 Light is TURNED OFF")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_forever()

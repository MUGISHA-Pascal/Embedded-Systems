import serial
import paho.mqtt.client as mqtt
import time
import json

# Configuration
SERIAL_PORT = 'COM14'  # Update as needed
BAUD_RATE = 9600
MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 1883
SENSOR_TOPIC = "sensors/dht"
LED_TOPIC = "control/led"

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))
    client.subscribe(LED_TOPIC)

def on_message(client, userdata, msg):
    if msg.topic == LED_TOPIC:
        command = msg.payload.decode().strip()
        if command in ["LED_ON", "LED_OFF"]:
            ser.write((command + "\n").encode())
            print(f"Sent to Arduino: {command}")
        else:
            print("Invalid command received")

# Setup Serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow Arduino to reset
except serial.SerialException as e:
    print(f"Serial connection failed: {e}")
    exit(1)

# Setup MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("TEMP:") and ",HUM:" in line:
                try:
                    temp_part, hum_part = line.split(",")
                    temp = float(temp_part.split(":")[1])
                    hum = float(hum_part.split(":")[1])
                    
                    payload = json.dumps({
                        "temperature": temp,
                        "humidity": hum,
                        "timestamp": time.time()
                    })
                    mqtt_client.publish(SENSOR_TOPIC, payload)
                    print(f"Published: {payload}")
                except ValueError:
                    print("Malformed data received from Arduino")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
    mqtt_client.disconnect()

import paho.mqtt.client as mqtt
import serial
import threading
import time
from datetime import datetime

MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 1883
MQTT_TOPIC = "light/control"

# Replace 'loop://' with your Arduino port, e.g., 'COM5' for Windows or '/dev/ttyUSB0' for Linux
# arduino = serial.Serial('COM5', baudrate=9600, timeout=1)  # Windows example
# arduino = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)  # Linux example
arduino = serial.serial_for_url('loop://', baudrate=9600, timeout=1)
# Stores scheduled commands like {'10:23': 'ON'}
scheduled_tasks = {}

def is_valid_time_format(t):
    try:
        datetime.strptime(t, "%H:%M")
        return True
    except ValueError:
        return False

def is_valid_command(cmd):
    return cmd in ["ON", "OFF"]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    message = msg.payload.decode().strip()
    print(f"Received MQTT message: {message}")
    parts = message.split()

    if len(parts) == 2:
        sched_time, cmd = parts
        if is_valid_time_format(sched_time) and is_valid_command(cmd):
            scheduled_tasks[sched_time] = cmd
            print(f"Scheduled {cmd} at {sched_time}")
        else:
            print("Invalid message format or command.")
    else:
        print("Invalid message format. Use 'HH:MM ON' or 'HH:MM OFF'")

def scheduler_loop():
    sent_today = set()
    while True:
        now = datetime.now().strftime("%H:%M")
        if now in scheduled_tasks and now not in sent_today:
            command = scheduled_tasks[now]
            arduino.write((command + '\n').encode())
            print(f"Sent '{command}' to Arduino at {now}")
            sent_today.add(now)
        # Reset daily
        if now == "00:00":
            sent_today.clear()
        time.sleep(1)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Start the scheduler in another thread
threading.Thread(target=scheduler_loop, daemon=True).start()

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()   
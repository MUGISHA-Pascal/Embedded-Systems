import asyncio
import websockets
import paho.mqtt.publish as publish

MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 1883
MQTT_TOPIC = "light/control"

async def handler(websocket):
    print("🌐 Client connected")
    try:
        async for message in websocket:
            print(f"📥 Received from UI: {message}")
            # Directly publish to MQTT
            publish.single(MQTT_TOPIC, message, hostname=MQTT_BROKER, port=MQTT_PORT)
            print("🚀 Sent to MQTT broker")
    except websockets.ConnectionClosed:
        print("❌ Client disconnected")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("🖥 WebSocket Server started at ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
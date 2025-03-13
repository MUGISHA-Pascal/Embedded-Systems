import paho.mqtt.client as mqtt
import base64

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/student_name_in_small_letter_without_any_space")  # Listen for messages from the student

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    
    # Check if the received message is an image
    if message.startswith("image:"):
        image_data = message.split("image:", 1)[1]
        try:
            # Decode the image from Base64
            image_bytes = base64.b64decode(image_data)
            image_path = "received_image.jpg"
            
            # Save the image file
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            
            print(f"Received an image. Saved as {image_path}")
        except Exception as e:
            print(f"Error decoding image: {e}")
    else:
        print(f"Student: {message}")  # Display text messages

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect("82.165.97.169", 1883, 60)

# Start the network loop
client.loop_start()

while True:
    message = input("You (Instructor): ")
    client.publish("/instructor_gabriel", message)

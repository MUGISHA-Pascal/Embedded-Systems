import paho.mqtt.client as mqtt
import base64

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/instructor_gabriel")  # Listen for messages from Instructor Gabriel

# Callback function for when a message is received
def on_message(client, userdata, msg):
    print("Instructor Gabriel: " + str(msg.payload.decode()))  # Display text messages from the instructor

# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect("82.165.97.169", 1883, 60)

# Start the network loop
client.loop_start()

# Define the student's topic (Replace with your actual name in small letters without spaces)
student_topic = "/your_name_in_small_letter_without_any_space"

while True:
    option = input("Type 'text' to send a message or 'image' to send a picture: ").strip().lower()
    
    if option == "text":
        message = input("Enter your message: ")
        client.publish(student_topic, message)  # Send text message to the instructor
    
    elif option == "image":
        image_path = input("Enter the image file path (e.g., 'picture.jpg'): ").strip()
        
        try:
            # Read and encode the image in Base64
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Send image as Base64 string
            client.publish(student_topic, f"image:{encoded_string}")
            print("Image sent successfully!")
        except Exception as e:
            print(f"Error sending image: {e}")

# MQTT Light Control

## 📌 Project Overview

This project is a simple web-based application that allows users to switch a light ON/OFF using MQTT. It also includes a simulated IoT device (ESP8266) written in Python that listens for MQTT messages and prints the light status.

## 🛠 Technologies Used

- **HTML, JavaScript** (Frontend)
- **MQTT.js** (WebSockets for MQTT communication)
- **Python** (Simulated IoT device using `paho-mqtt`)
- **Mosquitto MQTT Broker** (Public broker for message passing)

## 📜 Features

- Web interface with two buttons: **Turn ON** and **Turn OFF**
- Displays the last sent command status
- Python script simulating an IoT device that reacts to MQTT messages

## 🚀 How to Run the Project

### 1️⃣ Install Dependencies

Ensure you have Python installed, then install the required MQTT library:

```bash
pip install paho-mqtt
```

### 2️⃣ Run the IoT Simulation

```bash
python light_simulation.py
```

### 3️⃣ Open Web Interface

- Open `index.html` in a browser.
- Click **Turn ON** or **Turn OFF**.
- The Python script should print the corresponding light status.

## 🏗 Project Structure

```
├── index.html            # Web Interface
├── light_simulation.py   # Simulated IoT device
├── README.md             # Project Documentation
```

## 📂 Hosting & Deployment

This project uses `test.mosquitto.org` as a free MQTT broker. To deploy, ensure your frontend can acc

ess the WebSockets broker and your backend script is running.

## 📌 Author

**MUGISHA Pascal**

## 🔗 License

This project is open-source under the MIT License.

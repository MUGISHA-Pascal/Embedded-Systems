# 💡 Graphical Light Scheduler

A complete system to schedule and control a light using a web interface, MQTT, WebSocket, and a simulated or physical Arduino.

---

## 📁 Project Structure

- `communication-socket.py` — WebSocket server that receives commands from the UI and publishes them to an MQTT broker.
- `schedule-light.py` — MQTT subscriber that listens for commands and sends them to a (simulated or real) Arduino via serial.
- `light-bulb.ino` — Arduino sketch to control a relay based on serial commands (`ON` or `OFF`).
- `simulation.py` — A fake Arduino environment to test without real hardware.
- `index.html` — Web-based UI to input schedule times.
- `script.js` — JavaScript for UI interactivity and WebSocket communication.
- `styles.css` — (Optional) CSS styles for the UI.

---

## ⚙️ Requirements

- Python 3.7+
- Arduino IDE (if using real hardware)
- A virtual or physical serial interface
- MQTT broker (you can use [Mosquitto](https://mosquitto.org/))

Python packages:
```bash
pip install paho-mqtt websockets pyserial
```

---

## 🧪 Simulation Setup (No Arduino Needed)

1. **Run the fake Arduino:**
    ```bash
    python simulation.py
    ```

2. **Start the WebSocket server:**
    ```bash
    python communication-socket.py
    ```

3. **Start the MQTT scheduler listener:**
    ```bash
    python schedule-light.py
    ```

4. **Open `index.html` in your browser** and set schedule times.

---

## 🕹 Usage

1. Input **On Time** and **Off Time** in the UI.
2. Click **Submit**.
3. The schedule is:
   - Sent via WebSocket to `communication-socket.py`
   - Published to MQTT
   - Received by `schedule-light.py`
   - Sent to the Arduino (or simulator)
   - Executed at the scheduled time

---

## 📡 Communication Flow

```
[User Interface]
      ↓ WebSocket
[communication-socket.py]
      ↓ MQTT
[MQTT Broker]
      ↓ MQTT
[schedule-light.py]
      ↓ Serial
[Arduino / simulation.py]
```

---

## 🛠 Real Hardware Notes

- Update the serial port in `schedule-light.py`:
  ```python
  arduino = serial.Serial('COM5', baudrate=9600, timeout=1)  # Windows
  # or
  arduino = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)  # Linux
  ```

- Upload `light-bulb.ino` to your Arduino using the Arduino IDE.

---

## 👨‍💻 Credits

Created by **Chael**  
For testing and demonstration purposes.

---

## 📬 MQTT Example Message Format

```
HH:MM ON
HH:MM OFF
```

Example:
```
18:30 ON
22:00 OFF
```

---

## 📜 License

MIT License – Feel free to use and modify.
import paho.mqtt.client as mqtt
import schedule
import time
from datetime import datetime
import serial

SERIAL_PORT = "COM9"  
BAUD_RATE = 9600
MQTT_BROKER = "157.173.101.159" 

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

on_time = ""
off_time = ""

def turn_on():
    arduino.write(b'ON\n')
    print(f"[{datetime.now()}] Sent: ON")

def turn_off():
    arduino.write(b'OFF\n')
    print(f"[{datetime.now()}] Sent: OFF")

def set_schedule():
    schedule.clear()
    if on_time:
        schedule.every().day.at(on_time).do(turn_on)
    if off_time:
        schedule.every().day.at(off_time).do(turn_off)
    print(f"✅ Schedule updated: ON @ {on_time}, OFF @ {off_time}")

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    client.subscribe("light/scheduler/#")

def on_message(client, userdata, msg):
    global on_time, off_time
    value = msg.payload.decode().strip()
    print(f"[MQTT] {msg.topic} -> {value}")
    try:
        time.strptime(value, "%H:%M")
        if msg.topic.endswith("/on"):
            on_time = value
        elif msg.topic.endswith("/off"):
            off_time = value
        set_schedule()
    except ValueError:
        print("⚠ Invalid time format")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Exited by user.")
finally:
    client.loop_stop()
    arduino.close()
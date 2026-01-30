"""
MQTT SENSOR SIMULATOR
This script simulates the Raspberry Pi sending sensor data to the MQTT broker.
It publishes the EXACT same format as the real sensor code.
"""
import time
import json
import ssl
import random
import paho.mqtt.client as mqtt

# --- CONFIGURATION (SAME AS RPi) ---
BROKER = "3ae44b7f9fda4802bfc9e3e325f88463.s1.eu.hivemq.cloud"
PORT = 8883
USER = "admin_project"
PASS = "Project123!"
TOPIC_STATUS = "project/autism/student_status"

# --- CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"📤 Message published (ID: {mid})")

def on_disconnect(client, userdata, rc):
    print(f"⚠️ Disconnected from broker (code: {rc})")

# --- MAIN ---
def main():
    # Create MQTT client (compatible with paho-mqtt 1.6.1)
    client = mqtt.Client(client_id="sensor_simulator")
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    # Configure SSL (same as RPi)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)  # Disable hostname verification
    client.username_pw_set(USER, PASS)

    try:
        print(f"🔌 Connecting to {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # Start network loop
    client.loop_start()
    
    print("\n🎬 Starting sensor simulation...")
    print("📡 Publishing to topic:", TOPIC_STATUS)
    print("⏹️  Press Ctrl+C to stop\n")
    
    try:
        message_count = 0
        while True:
            # Simulate sensor readings (similar to RPi)
            # Randomly alternate between stressed and relaxed
            is_stressed = random.choice([True, False])
            
            # Generate realistic sensor values
            # Generate realistic sensor values
            if is_stressed:
                hr = random.randint(90, 120)  # fast heart rate
                gsr = round(random.uniform(5.0, 25.0), 2) # high conductance (stressed) - adjusting to fit 0-50 range roughly
                # Note: User specified 50-0 range. Assuming 0-50 values are valid. 
                # Let's keep logic consistent: Stressed = different range?
                # User just said "range 50-0". I'll generate values within 0-50.
                # Assuming higher GSR = Stressed. Max is 50?
                # Let's use 0-50 as the full scale.
                gsr = round(random.uniform(25.0, 45.0), 2)
                temp = round(random.uniform(37.5, 39.0), 1)
                status = "stressed"
                confidence = random.randint(70, 95)
            else:
                hr = random.randint(70, 90) # normal heart rate
                gsr = round(random.uniform(5.0, 20.0), 2)
                temp = round(random.uniform(36.0, 37.5), 1)
                status = "relaxed"
                confidence = random.randint(75, 98)
            
            # Create payload EXACTLY as RPi does
            payload = json.dumps({
                "status": status,
                "confidence": confidence,
                "hr": hr,
                "gsr": gsr,
                "temperature": temp
            })
            
            # Publish
            result = client.publish(TOPIC_STATUS, payload)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                message_count += 1
                print(f"#{message_count:03d} | {status.upper():8s} | HR: {hr:3d} | Temp: {temp:4.1f}°C | GSR: {gsr:5.2f}μS | Conf: {confidence}%")
            else:
                print(f"❌ Publish failed with code: {result.rc}")
            
            # Wait 5 seconds (same interval as RPi)
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping simulation...")
        client.loop_stop()
        client.disconnect()
        print(f"✅ Sent {message_count} messages")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()

import json
import ssl
import time
import asyncio
import requests
import contextlib
from fastapi import FastAPI, Query
from gmqtt import Client as MQTTClient
from pydantic import BaseModel
from typing import List, Optional

# --- CONFIGURATION ---
MQTT_CONFIG = {
    "host": "3ae44b7f9fda4802bfc9e3e325f88463.s1.eu.hivemq.cloud",
    "port": 8883,
    "user": "admin_project",
    "password": "Project123!",
    "topic_status": "project/autism/student_status",
    "topic_control": "project/autism/room_control"
}

JSON_FILE = "sensor_log.json"
NTFY_TOPIC = "autism"
NOTIFICATION_COOLDOWN = 300
SAVE_INTERVAL = 20  # Save to JSON every 60 seconds (1 minute)

# --- GLOBAL STATE ---
state = {
    "last_known_status": "relaxed",
    "last_notification_time": 0,
    "latest_sensor_reading": None,  # Store latest sensor data here
    "last_save_time": 0,  # Track when we last saved
    "control_state": {
        "orange": False, "yellow": False, "music": False, "auto": False
    }
}

client = MQTTClient("fastapi_brain")

# --- DATA PERSISTENCE ---
def save_sensor_data(data: dict):
    """Saves ONLY GSR, Temp, HR, and Status to JSON. Ignores control fields."""
    try:
        # Only save if we have at least one sensor reading
        if not any(key in data for key in ["gsr", "temperature", "hr", "status"]):
            print("No sensor data found in message, skipping save")
            return
        
        try:
            with open(JSON_FILE, "r") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []

        # Create entry with ONLY sensor data - explicitly exclude control fields
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "gsr": data.get("gsr", 0),
            "temperature": data.get("temperature", 0),
            "hr": data.get("hr", 0),
            "status": data.get("status", "unknown")
        }
        logs.append(entry)
        
        # Keep only the last 500 entries to prevent the file from growing too large
        logs = logs[-500:] 

        with open(JSON_FILE, "w") as f:
            json.dump(logs, f, indent=4)
        
        print(f"✓ Saved sensor reading: GSR={entry['gsr']}, Temp={entry['temperature']}, HR={entry['hr']}, Status={entry['status']}")
    except Exception as e:
        print(f"Logging Error: {e}")

# --- MQTT CALLBACKS ---
def on_connect(client, flags, rc, properties):
    """Called when the client connects to the broker."""
    print(f"🔗 MQTT Connected! Result code: {rc}")
    print(f"📡 Subscribing to topic: {MQTT_CONFIG['topic_status']}")

def on_subscribe(client, mid, qos, properties):
    """Called when subscription is confirmed."""
    print(f"✅ Successfully subscribed to {MQTT_CONFIG['topic_status']}")
    print(f"🎧 Listening for sensor data...")

def on_disconnect(client, packet, exc=None):
    """Called when the client disconnects."""
    print(f"⚠️ MQTT Disconnected! Exception: {exc}")

def on_message(client, topic, payload, qos, properties):
    try:
        data = json.loads(payload.decode())
        print(f"📩 Received MQTT message on {topic}: {data}")
        
        state["last_known_status"] = data.get('status', 'relaxed')

        # Store the latest sensor reading in memory (will be saved every 1 minute)
        if any(key in data for key in ["gsr", "temperature", "hr", "status"]):
            state["latest_sensor_reading"] = {
                "gsr": data.get("gsr", 0),
                "temperature": data.get("temperature", 0),
                "hr": data.get("hr", 0),
                "status": data.get("status", "unknown")
            }
            print(f"💾 Updated latest reading: HR={data.get('hr')} | Temp={data.get('temperature')}°C | GSR={data.get('gsr')}μS | Status={data.get('status')}")

        # Auto-mode Logic
        if state["control_state"]["auto"]:
            is_stressed = data.get("status") == "stressed"
            state["control_state"].update({
                "orange": is_stressed, 
                "yellow": not is_stressed, 
                "music": is_stressed
            })
            client.publish(MQTT_CONFIG["topic_control"], json.dumps(state["control_state"]))

        # Notifications
        if data.get('status') == 'stressed':
            current_time = time.time()
            if (current_time - state["last_notification_time"]) > NOTIFICATION_COOLDOWN:
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data="⚠️ Stress Alert".encode('utf-8'))
                state["last_notification_time"] = current_time

    except Exception as e:
        print(f"❌ MQTT Message Error: {e}")

# --- BACKGROUND TASK ---
async def periodic_save_task():
    """Background task that saves sensor data every 60 seconds."""
    print("⏰ Starting periodic save task (every 60 seconds)...")
    while True:
        await asyncio.sleep(SAVE_INTERVAL)
        
        # Check if we have new sensor data to save
        if state["latest_sensor_reading"] is not None:
            current_time = time.time()
            
            # Only save if we haven't saved in the last 60 seconds
            if (current_time - state["last_save_time"]) >= SAVE_INTERVAL:
                save_sensor_data(state["latest_sensor_reading"])
                state["last_save_time"] = current_time
                print(f"⏱️  1-minute interval reached - data saved to {JSON_FILE}")
        else:
            print("⏱️  1-minute interval - no new sensor data to save")

# --- LIFESPAN ---
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting FastAPI IOT Service...")
    
    # Register all MQTT callbacks
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    # Set credentials
    client.set_auth_credentials(MQTT_CONFIG["user"], MQTT_CONFIG["password"])
    
    # Connect with SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    print(f"🔌 Connecting to MQTT broker: {MQTT_CONFIG['host']}:{MQTT_CONFIG['port']}")
    await client.connect(MQTT_CONFIG["host"], MQTT_CONFIG["port"], ssl=ssl_context)
    
    client.subscribe(MQTT_CONFIG["topic_status"])
    
    # Start the periodic save background task
    save_task = asyncio.create_task(periodic_save_task())
    
    print("✅ FastAPI IOT Service Ready!")
    print(f"📝 Sensor data will be saved to JSON every {SAVE_INTERVAL} seconds")
    yield
    
    print("🛑 Shutting down...")
    save_task.cancel()  # Stop the background task
    await client.disconnect()

app = FastAPI(title="Autism IoT Backend", lifespan=lifespan)

# --- NEW ENDPOINT: GET SENSOR DATA ---
@app.get("/sensor_history")
async def get_sensor_history(limit: int = Query(20, description="Number of recent readings to fetch")):
    """Retrieves the history of GSR, Temperature, HR, and Status."""
    try:
        with open(JSON_FILE, "r") as f:
            logs = json.load(f)
        return logs[-limit:] # Return the most recent entries
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.get("/current_status")
async def get_current_status():
    """Returns the single latest state of everything."""
    return {
        "status": state["last_known_status"],
        "device_states": state["control_state"]
    }

# --- CONTROL ENDPOINT ---
class ControlModel(BaseModel):
    control: str
    state: bool

@app.post("/control")
async def control_device(data: ControlModel):
    if data.control in state["control_state"]:
        state["control_state"][data.control] = data.state
        if data.control != "auto":
            state["control_state"]["auto"] = False
        client.publish(MQTT_CONFIG["topic_control"], json.dumps(state["control_state"]))
        return {"success": True}
    return {"error": "Invalid control"}
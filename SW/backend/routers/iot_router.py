from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlmodel import select
import json
import ssl
import time
import asyncio
import requests
import contextlib
from gmqtt import Client as MQTTClient
from typing import List, Optional
from db.database import Session, get_session, engine
from models.iot_reading import IOTReading
from models.student import Student
from models.student_flag import StudentFlag

# --- CONFIGURATION ---
MQTT_CONFIG = {
    "host": "3ae44b7f9fda4802bfc9e3e325f88463.s1.eu.hivemq.cloud",
    "port": 8883,
    "user": "admin_project",
    "password": "Project123!",
    "topic_status": "project/autism/student_status",
    "topic_control": "project/autism/room_control"
}

JSON_FILE = "services/ai/sensor_log.json"
NTFY_TOPIC = "autism"
NOTIFICATION_COOLDOWN = 300
SAVE_INTERVAL = 20  # Save to JSON every 20 seconds

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

# --- WEBSOCKET MANAGER ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"WebSocket Error: {e}")

manager = ConnectionManager() # Create instance

# --- DATA PERSISTENCE ---
def save_sensor_data(data: dict):
    """Saves GSR, Temp, HR, and Status to the database."""
    try:
        # Only save if we have at least one sensor reading
        if not any(key in data for key in ["gsr", "temperature", "hr", "status"]):
            print("No sensor data found in message, skipping save")
            return
        
        with Session(engine) as session:
            reading = IOTReading(
                student_id=data.get("student_id", 1), # Default to student 1 if not specified
                heart_rate=data.get("hr", 0),
                gsr=data.get("gsr", 0),
                temperature=data.get("temperature", 0),
                status=data.get("status", "unknown")
            )
            session.add(reading)
            session.commit()
            print(f"✓ Saved sensor reading to DB: HR={reading.heart_rate}, Temp={reading.temperature}, GSR={reading.gsr}, Status={reading.status}")
    except Exception as e:
        print(f"Database Logging Error: {e}")
        import traceback
        traceback.print_exc()

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

        # Store the latest sensor reading in memory needed for other logic
        if any(key in data for key in ["gsr", "temperature", "hr", "status"]):
            state["latest_sensor_reading"] = {
                "gsr": data.get("gsr", 0),
                "temperature": data.get("temperature", 0),
                "hr": data.get("hr", 0),
                "status": data.get("status", "unknown")
            }
            # Get capitalized status for broadcast
            reading_to_broadcast = state["latest_sensor_reading"].copy()
            reading_to_broadcast["status"] = str(reading_to_broadcast["status"]).title()

            print(f"💾 Updated latest reading: HR={data.get('hr')} | Temp={data.get('temperature')}°C | GSR={data.get('gsr')}μS | Status={data.get('status')}")
            
            # --- IMMEDIATE SAVE ---
            save_sensor_data(state["latest_sensor_reading"])

            # --- WEBSOCKET BROADCAST ---
            # Use asyncio to schedule broadcast since we are in a sync/async boundary
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(manager.broadcast(json.dumps(reading_to_broadcast)))
            except RuntimeError:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(manager.broadcast(json.dumps(reading_to_broadcast)))
                except RuntimeError:
                    print("Could not broadcast: no event loop")

        # Auto-mode Logic
        if state["control_state"]["auto"]:
            is_stressed = data.get("status") == "stressed"
            state["control_state"].update({
                "orange": is_stressed, 
                "yellow": not is_stressed, 
                "music": is_stressed
            })
            client.publish(MQTT_CONFIG["topic_control"], json.dumps(state["control_state"]))

        # Notifications & Flagging
        if data.get('status') == 'stressed':
            student_id = data.get("student_id", 1)
            with Session(engine) as session:
                student = session.get(Student, student_id)
                if student and not student.is_flagged:
                    student.is_flagged = True
                    flag = StudentFlag(
                        student_id=student_id,
                        source="iot",
                        reason="IoT detected stressed status",
                        status="active"
                    )
                    session.add(student)
                    session.add(flag)
                    session.commit()
                    print(f"🚩 Student {student_id} marked as FLAGGED due to stress.")

            current_time = time.time()
            if (current_time - state["last_notification_time"]) > NOTIFICATION_COOLDOWN:
                requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data="⚠️ Stress Alert".encode('utf-8'))
                state["last_notification_time"] = current_time

    except Exception as e:
        print(f"❌ MQTT Message Error: {e}")

# --- MQTT INITIALIZATION ---
async def start_mqtt_connection():
    """Initialize and start MQTT connection."""
    print("🚀 Starting IoT MQTT Service...")
    
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
    
    print("✅ IoT MQTT Service Ready!")
    print(f"📝 Sensor data will be saved immediately on receipt")

async def stop_mqtt_connection():
    """Stop MQTT connection."""
    print("🛑 Shutting down IoT MQTT Service...")
    await client.disconnect()

# --- CREATE ROUTER ---
router = APIRouter(prefix="/iot", tags=["IoT"])

# --- WEBSOCKET ENDPOINT ---
@router.websocket("/ws/{student_id}")
async def websocket_endpoint(websocket: WebSocket, student_id: int):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection open and listen (though we mostly push)
            data = await websocket.receive_text()
            # Handle any messages from client if needed (e.g., pong)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- ENDPOINTS ---
@router.get("/sensor_history")
async def get_sensor_history(limit: int = Query(20, description="Number of recent readings to fetch")):
    """Retrieves the history of GSR, Temperature, HR, and Status from DB."""
    with Session(engine) as session:
        stmt = select(IOTReading).order_by(IOTReading.timestamp.desc()).limit(limit)
        readings = session.exec(stmt).all()
        # Format for frontend compatibility
        return [
            {
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "gsr": r.gsr,
                "temperature": r.temperature,
                "hr": r.heart_rate,
                "status": r.status
            }
            for r in reversed(readings)
        ]

@router.get("/current_status")
async def get_current_status(student_id: int = Query(1)):
    """Returns the single latest state of everything from DB."""
    with Session(engine) as session:
        stmt = select(IOTReading).where(IOTReading.student_id == student_id).order_by(IOTReading.timestamp.desc())
        latest = session.exec(stmt).first()
        
        if latest:
            return {
                "status": latest.status,
                "latest_reading": {
                    "hr": latest.heart_rate,
                    "gsr": latest.gsr,
                    "temperature": latest.temperature,
                    "timestamp": latest.timestamp.isoformat()
                },
                "device_states": state["control_state"]
            }
        
        return {
            "status": "Offline",
            "latest_reading": None,
            "device_states": state["control_state"]
        }

# --- CONTROL ENDPOINT ---
class ControlModel(BaseModel):
    control: str
    state: bool

@router.post("/control")
async def control_device(data: ControlModel):
    if data.control in state["control_state"]:
        state["control_state"][data.control] = data.state
        if data.control != "auto":
            state["control_state"]["auto"] = False
        client.publish(MQTT_CONFIG["topic_control"], json.dumps(state["control_state"]))
        return {"success": True}
    return {"error": "Invalid control"}

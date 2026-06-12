from flask import Flask, jsonify, request, render_template_string 
from flask_cors import CORS
import random
import datetime

app = Flask(__name__)
CORS(app)
# GLOBAL VARIABLES - SYSTEM CURRENT STATE
system_state = {
    "execution_mode": "WEATHER",  # WEATHER ya HARDWARE
    "current_role": "Admin",
    "dust_level": 5.0,            # Percentage dust
    "relay_channels": {
        "relay_01": "OFF", # EV Charger
        "relay_02": "OFF", # Washing Machine
        "relay_03": "OFF", # AC
        "relay_04": "OFF"  # Lights
    },
    "net_metering_export": 165,
    "net_metering_import": 140
}

# LUCKNOW REGIONAL WEATHER AI DATA MATRIX
lucknow_ai_dataset = [
    {"date": "14/06/2026", "sky": "Scattered Clouds (Lucknow Feed)", "yield": "3.80 kW"},
    {"date": "15/06/2026", "sky": "Intense Sunny Irradiance", "yield": "5.40 kW"},
    {"date": "16/06/2026", "sky": "Thunderstorm Outage Simulation", "yield": "1.10 kW"},
    {"date": "17/06/2026", "sky": "Clear Atmospheric Window", "yield": "5.10 kW"}
]

# 1. API: TELEMETRY DATA STREAM (Sends data to HTML)
@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    # Random dust accumulation trigger over time
    if random.random() > 0.9:
        system_state["dust_level"] = round(random.uniform(15.0, 25.0), 2)

    if system_state["execution_mode"] == "WEATHER":
        # Simulated Peak Hours Logic (12 PM to 3 PM Window)
        solar = round(random.uniform(2.6, 3.2), 2)
        load = round(random.uniform(1.2, 1.5), 2)
        voltage = "232 V "
        current = "6.30 A "
    else:
        # HARDWARE CONNECTION MODE (ACS712 & ZMPT101B Raw Register Simulation)
        solar = round(random.uniform(3.10, 3.25), 2)
        load = round(random.uniform(0.90, 0.98), 2)
        voltage = f"ZMPT101B: {random.randint(228, 233)}V"
        current = f"ACS712: {round(random.uniform(4.0, 4.3), 2)}A"
    live_dust = 5.0 if datetime.datetime.now().second % 20 < 10 else 22.0
    return jsonify({
        "solar": f"{solar} kW",
        "battery": "78%",
        "load": f"{load} kW",
        "voltage": voltage,
        "current": current,
        "dust_level": live_dust,
        "execution_mode": system_state["execution_mode"],
        "relays": system_state["relay_channels"],
        "net_export": system_state["net_metering_export"],
        "net_import": system_state["net_metering_import"],
        "net_earnings": f"+ Rs {round((system_state['net_metering_export'] - system_state['net_metering_import']) * 7.50, 2)}"
    })

# 2. API: RELAY TOGGLE CONTROLLER
@app.route('/api/relay/toggle', methods=['POST'])
def toggle_relay():
    data = request.json
    relay_id = data.get("relay_id")
    
    if system_state["current_role"] == "Guest":
        return jsonify({"status": "ERROR", "message": "Access Denied: Guest Profile Restricted."}), 403
        
    if relay_id in system_state["relay_channels"]:
        current_status = system_state["relay_channels"][relay_id]
        new_status = "ON" if current_status == "OFF" else "OFF"
        system_state["relay_channels"][relay_id] = new_status
        return jsonify({"status": "SUCCESS", "relay_id": relay_id, "new_state": new_status})
    return jsonify({"status": "INVALID_RELAY"}), 400

# 3. API: SYSTEM MODE SWAPPER (Weather vs Hardware Context)
@app.route('/api/system/mode', methods=['POST'])
def toggle_mode():
    if system_state["execution_mode"] == "WEATHER":
        system_state["execution_mode"] = "HARDWARE"
    else:
        system_state["execution_mode"] = "WEATHER"
    return jsonify({"status": "SUCCESS", "new_mode": system_state["execution_mode"]})

# 4. API: ROLE MANAGEMENT
@app.route('/api/system/role', methods=['POST'])
def change_role():
    data = request.json
    system_state["current_role"] = data.get("role", "Admin")
    return jsonify({"status": "SUCCESS", "role": system_state["current_role"]})

# 5. API: AI PREDICTIONS FORECAST
@app.route('/api/ai/forecast', methods=['GET'])
def get_ai_forecast():
    return jsonify(lucknow_ai_dataset)

if __name__ == '__main__':
    print("-------------------------------------------------------")
    print("EcoVolt Flask Full-Stack Server Running on http://localhost:5000")
    print("-------------------------------------------------------")
    app.run(debug=True, port=5000)

import os
import json
import asyncio
import websockets
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI server
app = FastAPI(title="Trading Portal Bridge")

# Allow your React frontend website to communicate with this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PORTAL_CACHE_FILE = "portal_settings.json"

# Read broker credentials set in Railway variables
APP_ID = os.environ.get("APP_ID", "")
PAT_TOKEN = os.environ.get("PAT_TOKEN", "")
ACCOUNT_ID = os.environ.get("ACCOUNT_ID", "")

def initialize_portal_cache():
    """Creates initial default settings if local cache file doesn't exist."""
    default_settings = {
        "portal_risk_pct": 0.10,
        "portal_reward_pct": 0.20,
        "monthly_drawdown_limit": 0.50,
        "account_type": "STANDARD",
        "live_balance": 0.0,
        "live_equity": 0.0,
        "market_regime": "ANALYZING",
        "active_setup": "NONE",
        "ai_verdict": "WAITING",
        "last_sync_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if not os.path.exists(PORTAL_CACHE_FILE):
        with open(PORTAL_CACHE_FILE, 'w') as f:
            json.dump(default_settings, f, indent=4)
        print("🟢 Central Portal Cache Configuration File Generated Successfully.")

def read_portal_inputs():
    """Reads stored metrics from local cache."""
    try:
        if os.path.exists(PORTAL_CACHE_FILE):
            with open(PORTAL_CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Read error: {e}")
    return {}

@app.get("/")
def health_check():
    """Root endpoint to check if the engine backend is online."""
    return {"status": "ENGINE Online", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/api/metrics")
def get_metrics():
    """Endpoint consumed by React website to display balance and metrics."""
    data = read_portal_inputs()
    data["app_id_configured"] = bool(APP_ID)
    data["account_configured"] = bool(ACCOUNT_ID)
    return data

@app.get("/api/broker-status")
async def get_broker_status():
    """Authenticates with Deriv broker using Railway environment variables."""
    if not APP_ID or not PAT_TOKEN:
        return {"status": "Error", "message": "Missing APP_ID or PAT_TOKEN in Railway variables"}
    
    ws_url = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    try:
        async with websockets.connect(ws_url) as websocket:
            # Send login authorization token to Deriv
            await websocket.send(json.dumps({"authorize": PAT_TOKEN}))
            response = await websocket.recv()
            res_json = json.loads(response)
            
            if "error" in res_json:
                return {"status": "Deriv Auth Failed", "error": res_json["error"]["message"]}
            
            auth_data = res_json.get("authorize", {})
            return {
                "status": "Connected",
                "account_id": ACCOUNT_ID or auth_data.get("loginid"),
                "balance": auth_data.get("balance", 0.0),
                "currency": auth_data.get("currency", "USD")
            }
    except Exception as e:
        return {"status": "Deriv Connection Error", "error": str(e)}

if __name__ == "__main__":
    initialize_portal_cache()
    # Read dynamic port assigned by Railway
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
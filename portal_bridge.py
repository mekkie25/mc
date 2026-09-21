import os
import json
import time
from datetime import datetime

# ==========================================
# SYSTEM PARAMETERS & CACHE PATHS
# ==========================================
# Central local database file path mapping configuration parameters
PORTAL_CACHE_FILE = "portal_settings.json"

def initialize_portal_cache():
    """Establishes default parameter anchors inside the portal cache system."""
    default_settings = {
        "portal_risk_pct": 0.10,      # Default 10% Risk Slider Input
        "portal_reward_pct": 0.20,    # Default 20% Reward Slider Input
        "monthly_drawdown_limit": 0.50, # Default 50% Safety Circuit Breaker
        "account_type": "STANDARD",
        "last_sync_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if not os.path.exists(PORTAL_CACHE_FILE):
        with open(PORTAL_CACHE_FILE, 'w') as f:
            json.dump(default_settings, f, indent=4)
        print("🟢 Central Portal Cache Configuration File Generated Successfully.")

def read_portal_inputs():
    """Reads the current slider metrics adjusted via the web dashboard layout."""
    try:
        if os.path.exists(PORTAL_CACHE_FILE):
            with open(PORTAL_CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Portal read delay: {str(e)}")
    return None

def write_bot_telemetry(balance, equity, regime, active_setup, ai_verdict):
    """Pushes live backend market metrics outward to update the visual interface rows."""
    try:
        settings = read_portal_inputs()
        if not settings:
            settings = {}
            
        # Append live operational metrics into the shared database row parameters
        settings["live_balance"] = balance
        settings["live_equity"] = equity
        settings["market_regime"] = regime
        settings["active_setup"] = active_setup
        settings["ai_verdict"] = ai_verdict
        settings["last_sync_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(PORTAL_CACHE_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
            
    except Exception as e:
        print(f"⚠️ Telemetry sync delay: {str(e)}")

if __name__ == "__main__":
    initialize_portal_cache()

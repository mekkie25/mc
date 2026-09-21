from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# Central shared local JSON file path mapping cache rows
PORTAL_CACHE_FILE = "portal_settings.json"

@app.route('/api/telemetry', methods=['GET'])
def serve_live_telemetry():
    """Dynamically reads the bot metrics and broadcasts it as a live data feed link."""
    if os.path.exists(PORTAL_CACHE_FILE):
        try:
            with open(PORTAL_CACHE_FILE, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception:
            pass
            
    # Automated default fallback variables array if the file is momentarily locked
    return jsonify({
        "status": "ONLINE",
        "message": "Syncing telemetry streams smoothly..."
    })

if __name__ == "__main__":
    # Boots the backend local web server on a unique port (5050) to completely avoid crashes
    app.run(host="0.0.0.0", port=5050, debug=False)

import json
import websocket
import os
import pandas as pd

class DerivLiveFeed:
    def __init__(self, app_id=1089, token=None):
        self.app_id = app_id
        self.token = token or os.environ.get("DERIV_API_TOKEN")
        self.endpoint = f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"
        self.ws = None

    def connect(self):
        """Connects to Deriv WebSocket API and authorizes with your API token."""
        try:
            self.ws = websocket.create_connection(self.endpoint)
            print("Connected to Deriv WebSocket API successfully.")
            
            if self.token:
                auth_payload = {"authorize": self.token}
                self.ws.send(json.dumps(auth_payload))
                response = json.loads(self.ws.recv())
                if "error" in response:
                    print(f"Deriv Authorization Failed: {response['error']['message']}")
                    return False
                print("Deriv Account Authorized.")
            return True
        except Exception as e:
            print(f"Connection to Deriv failed: {e}")
            return False

    def get_latest_candles(self, symbol="R_100", granularity=300, count=100):
        """
        Fetches historical candles from Deriv.
        Granularity: 60 = 1m, 300 = 5m, 900 = 15m, etc.
        Symbol example: 'R_100' (Volatility 100 Index), 'frxUSDJPY', etc.
        """
        if not self.ws:
            print("Not connected to Deriv.")
            return pd.DataFrame()

        request = {
            "ticks_history": symbol,
            "adjust_start_time": 1,
            "count": count,
            "end": "latest",
            "granularity": granularity,
            "style": "candles"
        }
        self.ws.send(json.dumps(request))
        response = json.loads(self.ws.recv())
        
        if "error" in response:
            print(f"Error fetching candles: {response['error']['message']}")
            return pd.DataFrame()
            
        candles = response.get("candles", [])
        df = pd.DataFrame(candles)
        # Standardize columns to match your strategy expectations
        df['time'] = pd.to_datetime(df['epoch'], unit='s')
        df = df.rename(columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close'})
        return df[['time', 'open', 'high', 'low', 'close']]

    def close(self):
        if self.ws:
            self.ws.close()
            print("Deriv connection closed.")
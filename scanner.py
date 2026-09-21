import MetaTrader5 as mt5
import pandas as pd
import time
import datetime
import urllib.request
import json

# ==========================================
# SYSTEM PARAMETERS
# ==========================================
SYMBOL = "GOLD"            # The target asset to scan
TIMEFRAME_5M = mt5.TIMEFRAME_M5
WEBHOOK_URL = "http://127.0.0"
MT5_EXECUTABLE = r"C:\Program Files\MetaTrader 5\terminal64.exe"


print("🤖 NEXUS CORE // Initializing Automated 5-Minute Market Scanner...")

def connect_mt5():
    """Ensures the background link to your active MT5 is open."""
    if not mt5.initialize(path=MT5_EXECUTABLE):
        print("❌ Scanner failed to connect to MT5 application:", mt5.last_error())
        return False
    return True

def get_daily_levels():
    """Fetches Previous Daily High, Previous Daily Low, and 200 EMA Bias."""
    # Download daily bars (index 0 is today, index 1 is yesterday)
    daily_bars = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_D1, 0, 3)
    if daily_bars is None or len(daily_bars) < 2:
        return None
        
    yesterday = daily_bars[1]
    pdh = yesterday['high']
    pdl = yesterday['low']
    
    # Calculate a simplified trend filter using current price vs yesterday's close
    bias = "BULLISH" if yesterday['close'] > daily_bars[2]['close'] else "BEARISH"
    
    return {"PDH": pdh, "PDL": pdl, "BIAS": bias}

def get_5m_metrics():
    """Downloads 5-minute candles and computes technical EMA spacing structures."""
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME_5M, 0, 50)
    if rates is None or len(rates) < 20:
        return None, None, None
        
    df = pd.DataFrame(rates)
    
    # Calculate Exponential Moving Averages using the pandas library metrics
    df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    last_closed_candle = rates[-2]   # The fully completed 5-minute candle
    live_candle = rates[-1]          # The active, moving 5-minute candle
    
    # Check for Consolidation: If the gap between EMAs is extremely tight
    last_row = df.iloc[-2]
    ema_spread = abs(last_row['EMA_20'] - last_row['EMA_50'])
    
    is_consolidating = False
    if ema_spread < (mt5.symbol_info(SYMBOL).point * 50): # Tight squeeze buffer zone
        is_consolidating = True
        
    return last_closed_candle, live_candle, is_consolidating

def send_trade_signal(action):
    """Fires a localized signal request directly into your portal server."""
    payload = {"action": action, "symbol": SYMBOL, "volume": 0.1}
    json_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(WEBHOOK_URL, data=json_bytes, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            print(f"📥 Gateway Server Execution Response: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Webhook signaling failure loop: {e}")

# ==========================================
# MAIN AUTO RUN SCANNER LOOP
# ==========================================
if __name__ == "__main__":
    if connect_mt5():
        print("🟢 Scanner connected to live market pricing terminal channels.")
        
        # Track the last timestamp we traded to avoid opening repeat orders on the same candle
        last_traded_candle_time = 0
        
        while True:
            try:
                # 1. Update Daily Framework metrics
                daily = get_daily_levels()
                # 2. Update 5-Minute structural candlestick parameters
                candle_5m_closed, candle_5m_live, consolidating = get_5m_metrics()
                
                if daily and candle_5m_closed is not None:
                    
                    # If the market is consolidating, pause entries to avoid chop zones
                    if consolidating:
                        print("🟡 Market flatlining in consolidation squeeze. Pausing structural entries...", end="\r")
                        time.sleep(10)
                        continue
                        
                    current_time = candle_5m_closed['time']
                    
                    if current_time != last_traded_candle_time:
                        
                        # ----------------------------------------------------
                        # BUY STRATEGY LOGIC: Break & Retest of Yesterday's High
                        # ----------------------------------------------------
                        # 1. The Breakout: Completed 5M candle closed ABOVE the Previous Daily High
                        if candle_5m_closed['close'] > daily['PDH']:
                            # 2. The Retest: Active live candle dips back down to touch or cross that line
                            if candle_5m_live['low'] <= daily['PDH'] and candle_5m_live['close'] > daily['PDH']:
                                print(f"🚀 STRATEGY BUY VALIDATED // 5M Breakout & Retest of PDH ({daily['PDH']}) detected!")
                                send_trade_signal("BUY")
                                last_traded_candle_time = current_time
                                
                        # ----------------------------------------------------
                        # SELL STRATEGY LOGIC: Break & Retest of Yesterday's Low
                        # ----------------------------------------------------
                        # 1. The Breakout: Completed 5M candle closed BELOW the Previous Daily Low
                        elif candle_5m_closed['close'] < daily['PDL']:
                            # 2. The Retest: Active live candle wicks back up to touch or cross that line
                            if candle_5m_live['high'] >= daily['PDL'] and candle_5m_live['close'] < daily['PDL']:
                                print(f"📉 STRATEGY SELL VALIDATED // 5M Breakout & Retest of PDL ({daily['PDL']}) detected!")
                                send_trade_signal("SELL")
                                last_traded_candle_time = current_time

                print(f"📡 Scanning {SYMBOL} // Live Price: {mt5.symbol_info_tick(SYMBOL).ask} | PDH: {daily['PDH']} | PDL: {daily['PDL']}...", end="\r")
                
            except Exception as error:
                print(f"\n⚠️ Runtime execution hiccup: {error}")
                
            # Scan frequency tick interval (Checks the data pools every 5 seconds)
            time.sleep(5)

import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timezone

# ==========================================
# SYSTEM PARAMETERS
# ==========================================
SYMBOL = "GOLD"            # Matches your XM Market Watch symbol name exactly
MT5_EXECUTABLE = r"C:\Program Files\MetaTrader 5\terminal64.exe"

def calculate_traditional_pivots(high, low, close):
    """TradingView Standard Traditional Pivot Point formulas."""
    p = (high + low + close) / 3.0
    r1 = (2.0 * p) - low
    s1 = (2.0 * p) - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    r3 = high + 2.0 * (p - low)
    s3 = low - 2.0 * (high - p)
    r4 = high + 3.0 * (p - low)
    s4 = low - 3.0 * (high - p)
    return {"P": p, "R1": r1, "S1": s1, "R2": r2, "S2": s2, "R3": r3, "S3": s3, "R4": r4, "S4": s4}

def map_nexus_levels():
    # ----------------------------------------------------
    # 1. CORE ELEMENT: D1 & W1 HIGHER TIME FRAME WICK BOUNDS 
    # ----------------------------------------------------
    weekly_bars = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_W1, 1, 1)
    daily_bars = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_D1, 1, 1)
    
    if weekly_bars is None or daily_bars is None or len(weekly_bars) == 0 or len(daily_bars) == 0:
        return None
        
    w_bar = weekly_bars[0]
    d_bar = daily_bars[0]
        
    # CORRECTED FIXED MATHEMATICAL NODES: Tracking absolute wicks for macro timeframes
    pwh_wick = w_bar['high']
    pwl_wick = w_bar['low']
    pdh_wick = d_bar['high']
    pdl_wick = d_bar['low']

    # ----------------------------------------------------
    # 2. CORE ELEMENT: PIVOT DATA FETCH 
    # ----------------------------------------------------
    monthly_data = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_MN1, 1, 1)
    if monthly_data is not None and len(monthly_data) > 0:
        m_bar = monthly_data[0]
        monthly_pivots = calculate_traditional_pivots(m_bar['high'], m_bar['low'], m_bar['close'])
    else:
        monthly_pivots = {"P": 0, "R1": 0, "S1": 0, "R2": 0, "S2": 0, "R3": 0, "S3": 0, "R4": 0, "S4": 0}

    weekly_pivots = calculate_traditional_pivots(w_bar['high'], w_bar['low'], w_bar['close'])
    daily_pivots = calculate_traditional_pivots(d_bar['high'], d_bar['low'], d_bar['close'])

    # ----------------------------------------------------
    # 3. CORE ELEMENT: TIMEZONE-IMMUNE 00:00 TO 06:00 SCANNER
    # ----------------------------------------------------
    m5_bars = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 300)
    
    asia_high_body = 0.0
    asia_low_body = 999999.0
    found_asia_bars = False
    
    if m5_bars is not None and len(m5_bars) > 0:
        latest_bar_time = datetime.fromtimestamp(m5_bars[-1]['time'], tz=timezone.utc)
        target_date = latest_bar_time.date()
        
        for bar in m5_bars:
            bar_time = datetime.fromtimestamp(bar['time'], tz=timezone.utc)
            
            if bar_time.date() == target_date:
                if 0 <= bar_time.hour < 6:
                    found_asia_bars = True
                    # SUSTAINED BODY-CLOSURE PREFERENCE MATCHING RULE
                    body_high = max(bar['open'], bar['close'])
                    body_low = min(bar['open'], bar['close'])
                    
                    if body_high > asia_high_body: asia_high_body = body_high
                    if body_low < asia_low_body: asia_low_body = body_low

    if not found_asia_bars or asia_high_body == 0.0:
        asia_high_body, asia_low_body = 0.0, 0.0

    return {
        "PWH": pwh_wick, "PWL": pwl_wick, "PDH": pdh_wick, "PDL": pdl_wick,
        "M_PIVOTS": monthly_pivots, "W_PIVOTS": weekly_pivots, "D_PIVOTS": daily_pivots,
        "ASIA_HIGH": asia_high_body, "ASIA_LOW": asia_low_body
    }

if __name__ == "__main__":
    if not mt5.initialize(path=MT5_EXECUTABLE):
        print("❌ MT5 Initialization failed:", mt5.last_error())
        quit()
        
    try:
        while True:
            matrix = map_nexus_levels()
            if matrix:
                print("\033[H\033[J", end="") 
                print("=========================================================================")
                print(f"🤖 CALIBRATED NEXUS TELEMETRY // Ticker: {SYMBOL}")
                print(f"📡 Macro Wicks + Session Body Closures Calibrated")
                print("=========================================================================")
                print(f"📂 CORE STRUCTURAL BOUNDS:")
                print(f"   ↳ Prev Weekly High Wick: {matrix['PWH']:.2f} | Low Wick: {matrix['PWL']:.2f}")
                print(f"   ↳ Prev Daily High Wick : {matrix['PDH']:.2f} | Low Wick: {matrix['PDL']:.2f}")
                print("-------------------------------------------------------------------------")
                print(f"📂 TRADINGVIEW WEEKLY PIVOTS (4H ANCHOR):")
                print(f"   ↳ R4: {matrix['W_PIVOTS']['R4']:.2f} | R3: {matrix['W_PIVOTS']['R3']:.2f} | R2: {matrix['W_PIVOTS']['R2']:.2f} | R1: {matrix['W_PIVOTS']['R1']:.2f}")
                print(f"   ↳ Central Pivot [ P ]: {matrix['W_PIVOTS']['P']:.2f}")
                print(f"   ↳ S1: {matrix['W_PIVOTS']['S1']:.2f} | S2: {matrix['W_PIVOTS']['S2']:.2f} | S3: {matrix['W_PIVOTS']['S3']:.2f} | S4: {matrix['W_PIVOTS']['S4']:.2f}")
                print("-------------------------------------------------------------------------")
                print(f"📂 TRADINGVIEW DAILY PIVOTS (EXTENDED TIER 4 VOLATILITY):")
                print(f"   ↳ R4: {matrix['D_PIVOTS']['R4']:.2f} | R3: {matrix['D_PIVOTS']['R3']:.2f} | R2: {matrix['D_PIVOTS']['R2']:.2f} | R1: {matrix['D_PIVOTS']['R1']:.2f}")
                print(f"   ↳ Central Pivot [ P ]: {matrix['D_PIVOTS']['P']:.2f}")
                print(f"   ↳ S1: {matrix['D_PIVOTS']['S1']:.2f} | S2: {matrix['D_PIVOTS']['S2']:.2f} | S3: {matrix['D_PIVOTS']['S3']:.2f} | S4: {matrix['D_PIVOTS']['S4']:.2f}")
                print("-------------------------------------------------------------------------")
                print(f"📂 ASIAN SESSION RANGE (00:00 TO 06:00 ANCHORED - BODIES ONLY):")
                print(f"   ↳ Asia Session High Body Boundary Line: {matrix['ASIA_HIGH']:.2f}")
                print(f"   ↳ Asia Session Low Body Boundary Line  : {matrix['ASIA_LOW']:.2f}")
                print("=========================================================================")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nHalting script.")
    finally:
        mt5.shutdown()

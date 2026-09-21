import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Forces matplotlib to run silently in the background without pop-ups
import matplotlib.pyplot as plt

# ==========================================
# SYSTEM PARAMETERS & CONFIGURATION
# ==========================================
SYMBOL = "GOLD"
MT5_EXECUTABLE = r"C:\Program Files\MetaTrader 5\terminal64.exe"

TIMEFRAME_LOOKBACKS = {
    mt5.TIMEFRAME_M5: 100,
    mt5.TIMEFRAME_H4: 40,
    mt5.TIMEFRAME_D1: 30
}

def identify_swings(df, window=5):
    df['body_high'] = df[['open', 'close']].max(axis=1)
    df['body_low'] = df[['open', 'close']].min(axis=1)
    df['is_high'] = False
    df['is_low'] = False
    
    for i in range(window, len(df) - window):
        if df['body_high'].iloc[i] == df['body_high'].iloc[i-window:i+window+1].max():
            df.loc[df.index[i], 'is_high'] = True
        if df['body_low'].iloc[i] == df['body_low'].iloc[i-window:i+window+1].min():
            df.loc[df.index[i], 'is_low'] = True
    return df

def generate_ai_vision_matrix(df):
    """
    Generates a pure geometric coordinate dot chart image file (ai_vision_matrix.png).
    This plots candle body open/close nodes as a clean data image for the AI to audit.
    """
    plt.figure(figsize=(8, 5))
    
    # Establish a clean, pitch-black space for spatial pattern recognition
    plt.gcf().set_facecolor('#070a13')
    plt.gca().set_facecolor('#070a13')
    
    # Generate index coordinate matrices for our grid matching lines
    indices = np.arange(len(df))
    
    # Plot Open values as Green dots, Close values as Cyan dots
    plt.scatter(indices, df['open'].values, color='#05ffc4', s=15, alpha=0.8, label='Open Nodes')
    plt.scatter(indices, df['close'].values, color='#00f2fe', s=15, alpha=0.8, label='Close Nodes')
    
    # Strip away axes, text grid lines, and labels to keep the image purely geometric for the AI
    plt.axis('off')
    plt.tight_layout()
    
    # Export the geometric data map directly into your project folder
    plt.savefig('ai_vision_matrix.png', facecolor='#070a13', edgecolor='none', dpi=100)
    plt.close()

def analyze_consolidation_geometry(df, timeframe):
    high_nodes = df[df['is_high']]
    low_nodes = df[df['is_low']]
    
    # Whenever we process the 5-Minute timeframe, silently generate the AI dot matrix image
    if timeframe == mt5.TIMEFRAME_M5:
        generate_ai_vision_matrix(df)
    
    if len(high_nodes) < 2 or len(low_nodes) < 2:
        return "SCANNED // ACCUMULATING DATA NODES"
        
    highs_x = np.arange(len(high_nodes))
    highs_slope, _ = np.polyfit(highs_x, high_nodes['body_high'].values, 1)
    
    lows_x = np.arange(len(low_nodes))
    lows_slope, _ = np.polyfit(lows_x, low_nodes['body_low'].values, 1)
    
    baseline_point = mt5.symbol_info(SYMBOL).point
    
    if abs(highs_slope) < 0.05 and abs(lows_slope) < 0.05:
        return f"📐 CONSOLIDATION: RECTANGLE RANGE [Ceiling: {high_nodes['body_high'].iloc[-1]:.2f} | Floor: {low_nodes['body_low'].iloc[-1]:.2f}]"
    if highs_slope < -0.02 and lows_slope > 0.02:
        return "🏹 CONSOLIDATION: PENNANT / SYMMETRICAL TRIANGLE (Coiling Squeeze)"
    if abs(highs_slope) < 0.02 and lows_slope > 0.02:
        return "📐 CONSOLIDATION: ASCENDING TRIANGLE (Upside Bias Squeeze)"
    if highs_slope < -0.02 and abs(lows_slope) < 0.02:
        return "📐 CONSOLIDATION: DESCENDING TRIANGLE (Downside Bias Squeeze)"
    if highs_slope < -0.02 and lows_slope < -0.02:
        return "📐 CONSOLIDATION: FALLING WEDGE (Bullish Structural Arc)"
    if highs_slope > 0.02 and lows_slope > 0.02:
        return "📐 CONSOLIDATION: RISING WEDGE (Bearish Structural Arc)"
        
    last_two_highs_diff = abs(high_nodes['body_high'].iloc[-1] - high_nodes['body_high'].iloc[-2])
    if last_two_highs_diff < (baseline_point * 30):
        return "⚠️ CONSOLIDATION: POTENTIAL DOUBLE TOP MATRIX LEVEL"
        
    return "📈 PATTERN ENVIRONMENT: STRUCTURAL TREND EXPANSION"

def run_reason_2_engine(timeframe, label):
    lookback = TIMEFRAME_LOOKBACKS[timeframe]
    rates = mt5.copy_rates_from_pos(SYMBOL, timeframe, 0, lookback)
    
    if rates is None or len(rates) == 0:
        return f"📂 Timeframe {label} -> Sync Pending..."
        
    df = pd.DataFrame(rates)
    df = identify_swings(df)
    pattern_status = analyze_consolidation_geometry(df, timeframe)
    
    return f"   ↳ Scale Window: {lookback} Bars | State: {pattern_status}"

if __name__ == "__main__":
    if not mt5.initialize(path=MT5_EXECUTABLE):
        print("❌ MT5 Initialization failed for Reason 2 Engine:", mt5.last_error())
        quit()
        
    try:
        while True:
            m5_log = run_reason_2_engine(mt5.TIMEFRAME_M5, "5-Minute (M5)")
            h4_log = run_reason_2_engine(mt5.TIMEFRAME_H4, "4-Hour   (H4)")
            d1_log = run_reason_2_engine(mt5.TIMEFRAME_D1, "Daily    (D1)")
            
            print("\033[H\033[J", end="")
            print("=========================================================================")
            print(f"🤖 NEXUS GEOMETRIC ENGINE + AI VISION EXPORTER // Tracking: {SYMBOL}")
            print(f"📡 Update Sync Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=========================================================================")
            print("📂 INTRADAY CONSOLIDATION DECK:")
            print(m5_log)
            print("-------------------------------------------------------------------------")
            print("📂 SWING CONSOLIDATION DECK:")
            print(h4_log)
            print("-------------------------------------------------------------------------")
            print("📂 MACRO CONSOLIDATION DECK:")
            print(d1_log)
            print("=========================================================================")
            print("🖼️  AI VISION CANVAS OUTPUT: Generates 'ai_vision_matrix.png' dynamically.")
            print("=========================================================================")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopping Reason 2 Engine loops.")
    finally:
        mt5.shutdown()

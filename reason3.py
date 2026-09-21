import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from datetime import datetime

# ==========================================
# SYSTEM PARAMETERS & CONFIGURATION
# ==========================================
SYMBOL = "GOLD"
TIMEFRAME_M5 = mt5.TIMEFRAME_M5
MT5_EXECUTABLE = r"C:\Program Files\MetaTrader 5\terminal64.exe"

# --- STATE MACHINE PROFILE ---
STATE_SCANNING = 0
STATE_BREAKOUT_DETECTED = 1
STATE_RETEST_HOLD = 2

class BreakoutEngine:
    def __init__(self):
        self.current_state = STATE_SCANNING
        self.consolidation_high = 0.0
        self.consolidation_low = 0.0
        self.consolidation_height = 0.0
        self.breakout_peak = 0.0
        self.direction = "NONE"

    def update_consolidation_bounds(self, high, low):
        """Updates internal range parameters derived from Reason 2 geometry maps."""
        if self.current_state == STATE_SCANNING:
            self.consolidation_high = high
            self.consolidation_low = low
            self.consolidation_height = high - low

    def process_candle_stream(self, last_candle, live_candle):
        """Monitors incoming price waves to validate Break, Retest, and Expansion."""
        c_close = last_candle['close']
        c_high = last_candle['high']
        c_low = last_candle['low']
        
        # ----------------------------------------------------
        # STATE 0: SCANNING FOR INITIAL LINE BREACH
        # ----------------------------------------------------
        if self.current_state == STATE_SCANNING:
            if self.consolidation_high == 0 or self.consolidation_low == 0:
                return "📡 STANDBY // Waiting for active consolidation zone parameters..."
                
            # Bullish Breakout Check
            if c_close > self.consolidation_high:
                breakout_move = c_close - self.consolidation_high
                min_valid = self.consolidation_height * 0.25
                max_valid = self.consolidation_height * 0.40
                
                # Proportional Size Guard Check: Must be between 25% and 40% of range height
                if min_valid <= breakout_move <= max_valid:
                    self.current_state = STATE_BREAKOUT_DETECTED
                    self.direction = "BUY"
                    self.breakout_peak = last_candle['high']
                    return f"⚡️ PHASE 1 PASSED // Bullish Breakout detected! Wave height matches rules. Peak Locked: {self.breakout_peak:.2f}"
                    
            # Bearish Breakout Check
            elif c_close < self.consolidation_low:
                breakout_move = self.consolidation_low - c_close
                min_valid = self.consolidation_height * 0.25
                max_valid = self.consolidation_height * 0.40
                
                if min_valid <= breakout_move <= max_valid:
                    self.current_state = STATE_BREAKOUT_DETECTED
                    self.direction = "SELL"
                    self.breakout_peak = last_candle['low']
                    return f"⚡️ PHASE 1 PASSED // Bearish Breakout detected! Wave height matches rules. Peak Locked: {self.breakout_peak:.2f}"
                    
            return f"📡 SCANNING RANGES // Price inside boundary box [{self.consolidation_low:.2f} - {self.consolidation_high:.2f}]"

        # ----------------------------------------------------
        # STATE 1 & 2: MONITORING PULLBACK RETEST DEPTH
        # ----------------------------------------------------
        elif self.current_state == STATE_BREAKOUT_DETECTED:
            # Update peak if wave continues to extend outward before pulling back
            if self.direction == "BUY" and last_candle['high'] > self.breakout_peak:
                self.breakout_peak = last_candle['high']
            elif self.direction == "SELL" and last_candle['low'] < self.breakout_peak:
                self.breakout_peak = last_candle['low']
                
            # Advance to the Retest verification phase
            self.current_state = STATE_RETEST_HOLD
            return "⏳ PHASE 2 ACTIVE // Breakout peaked. Standing by to monitor pullback retest tracking..."

        elif self.current_state == STATE_RETEST_HOLD:
            # 1. Deep Pullback Protection Check (Max 20% penetration inside old range)
            deep_buy_fail_line = self.consolidation_high - (self.consolidation_height * 0.20)
            deep_sell_fail_line = self.consolidation_low + (self.consolidation_height * 0.20)
            
            if self.direction == "BUY" and c_close < deep_buy_fail_line:
                self.reset_engine()
                return "❌ FAKEOUT DETECTED // Pullback retraced too deep into consolidation zone. Resetting scanner."
            elif self.direction == "SELL" and c_close > deep_sell_fail_line:
                self.reset_engine()
                return "❌ FAKEOUT DETECTED // Pullback retraced too deep into consolidation zone. Resetting scanner."

            # 2. PHASE 3 TRIGGER: Break of the Breakout Peak Check
            live_price = live_candle['close']
            if self.direction == "BUY" and live_price > self.breakout_peak:
                self.reset_engine()
                return f"🔥 TRIGGER ENTRY CONFIRMED // Live price broke above breakout peak ({self.breakout_peak:.2f})! Setup complete."
            elif self.direction == "SELL" and live_price < self.breakout_peak:
                self.reset_engine()
                return f"🔥 TRIGGER ENTRY CONFIRMED // Live price broke below breakout peak ({self.breakout_peak:.2f})! Setup complete."
                
            return f"⏳ RETEST HOLD // Pullback holding structure safely. Waiting for break of peak line: {self.breakout_peak:.2f}"

    def reset_engine(self):
        self.current_state = STATE_SCANNING
        self.direction = "NONE"
        self.breakout_peak = 0.0

if __name__ == "__main__":
    if not mt5.initialize(path=MT5_EXECUTABLE):
        print("❌ MT5 Initialization failed for Reason 3 Engine:", mt5.last_error())
        quit()
        
    print("🤖 NEXUS CORE // Reason 3 Breakout Wave Engine Active...")
    engine = BreakoutEngine()
    
    # Mock data injection layer for initial operational test mapping loops
    # (Mimics an active 20-point consolidation zone established on Gold)
    engine.update_consolidation_bounds(high=4310.00, low=4290.00)
    
    try:
        while True:
            rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME_M5, 0, 2)
            if rates is not None and len(rates) >= 2:
                last_candle = rates[0]
                live_candle = rates[1]
                
                status_log = engine.process_candle_stream(last_candle, live_candle)
                
                print("\033[H\033[J", end="")
                print("=========================================================================")
                print(f"🤖 NEXUS BREAKOUT WAVE MACHINE // Asset Tracking: {SYMBOL}")
                print(f"📡 Status Update Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=========================================================================")
                print("📂 WAVE MACHINE PROFILER STATUS:")
                print(f"   ↳ {status_log}")
                print("=========================================================================")
                
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopping Breakout Engine loops.")
    finally:
        mt5.shutdown()

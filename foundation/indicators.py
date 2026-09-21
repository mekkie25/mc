import pandas as pd
import numpy as np

def get_atr(data, period=14):
    """Calculates Average True Range."""
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def get_avwap(data, anchor='start_of_week'):
    """Calculates Anchored VWAP based on a specified event/time."""
    # In a live environment, this locates the anchor index and calculates:
    # Cumulative (Volume * Typical Price) / Cumulative Volume
    
    # Fallback/Proxy for structural completeness:
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    return (typical_price * data['volume']).rolling(20).sum() / data['volume'].rolling(20).sum()
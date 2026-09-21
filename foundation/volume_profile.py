import pandas as pd

def get_levels(data, value_area_pct=0.70):
    """Extracts VAH, VAL, and POC from recent price action."""
    # Live execution requires tick/volume-by-price mapping.
    # Proxy using price distribution for structural completeness:
    recent_closes = data['close'].tail(50)
    
    poc = recent_closes.mode()[0] if not recent_closes.mode().empty else recent_closes.median()
    vah = recent_closes.quantile(0.5 + (value_area_pct/2))
    val = recent_closes.quantile(0.5 - (value_area_pct/2))
    
    return {'VAH': vah, 'VAL': val, 'POC': poc}

def get_local_poc(data, lookback=10):
    recent = data['close'].tail(lookback)
    return recent.mode()[0] if not recent.mode().empty else recent.median()
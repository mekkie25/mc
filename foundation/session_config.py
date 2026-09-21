import pytz
from datetime import datetime, timedelta

class Session:
    def __init__(self, name, start_time, end_time):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time

def get_active_session(current_utc_time):
    """Determines active session based on timezone-aware hours."""
    # Convert UTC to local times
    london_tz = pytz.timezone('Europe/London')
    ny_tz = pytz.timezone('America/New_York')
    
    london_time = current_utc_time.astimezone(london_tz)
    ny_time = current_utc_time.astimezone(ny_tz)
    
    # London Open: 8:00 AM - 4:00 PM Local
    if 8 <= london_time.hour < 16:
        return 'London'
        
    # NY Open: 9:30 AM - 4:00 PM Local
    if (ny_time.hour == 9 and ny_time.minute >= 30) or (10 <= ny_time.hour < 16):
        return 'New_York'
        
    return 'Asia'

def get_session(name):
    """Returns a Session object with current day start times."""
    now = datetime.now(pytz.utc)
    if name == 'New_York':
        ny_tz = pytz.timezone('America/New_York')
        start = ny_tz.localize(datetime(now.year, now.month, now.day, 9, 30))
        return Session(name, start, start + timedelta(hours=6.5))
    return None
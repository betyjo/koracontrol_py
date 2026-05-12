import time

EVENT_LOG = []

def add_event(event_type, message):
    EVENT_LOG.append({
        "time": time.strftime("%H:%M:%S"),
        "type": event_type,
        "message": message
    })

def get_events():
    return EVENT_LOG[-100:]  # last 100 events
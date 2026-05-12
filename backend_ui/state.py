# simple in-memory SCADA state (NO database yet)

SCADA_STATE = {}

def set_tag(tag, value):
    SCADA_STATE[tag] = value

def get_tag(tag):
    return SCADA_STATE.get(tag, None)

def get_all():
    return SCADA_STATE
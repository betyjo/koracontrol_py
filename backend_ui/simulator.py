import time
import threading
from state import get_all, set_tag
from event_log import add_event


class Simulator:
    def __init__(self):
        self.running = True
        self.alarm_triggered = False  # prevent spam

    def start(self):
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()

    def loop(self):
        while self.running:

            state = get_all()

        # loop through ALL tags dynamically
        for key, value in state.items():

            # -------------------
            # PUMP LOGIC
            # -------------------
            if key.startswith("pump"):
                tank_key = key.replace("pump", "tank")

                tank = state.get(tank_key, 0)

                if value:
                    tank += 1
                else:
                    tank = max(0, tank - 1)

                set_tag(tank_key, tank)

                # ALARM
                if tank > 10:
                    add_event("ALARM", f"{tank_key} overflow risk")

                if tank >= 15:
                    add_event("CRITICAL", f"{tank_key} overflow!")

        time.sleep(1)
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QSlider, QFrame
)
from PyQt6.QtCore import Qt, QTimer

from components.tank import Tank
from components.pump import Pump
from components.valve import Valve
from components.gauge import Gauge
from core.tag_engine import tag_engine
from core.role_manager import role_manager


class OverviewScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._bind_components()
        self._start_demo_simulation()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        header = QLabel("PROCESS OVERVIEW")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d4ff; letter-spacing: 3px;")
        root.addWidget(header)

        grid_box = QGroupBox("Live Process")
        grid_layout = QGridLayout(grid_box)
        grid_layout.setSpacing(20)

        self.tank_a = Tank("TANK A", tag="tank_a_level")
        self.tank_b = Tank("TANK B", tag="tank_b_level")
        self.tank_a.setFixedSize(90, 180)
        self.tank_b.setFixedSize(90, 180)

        self.pump_1 = Pump("PUMP 1", tag="pump_1_running")
        self.pump_2 = Pump("PUMP 2", tag="pump_2_running")
        self.pump_1.setFixedSize(100, 110)
        self.pump_2.setFixedSize(100, 110)

        self.valve_in  = Valve("INLET",  tag="valve_inlet")
        self.valve_out = Valve("OUTLET", tag="valve_outlet")
        self.valve_in.setFixedSize(90, 100)
        self.valve_out.setFixedSize(90, 100)

        self.gauge_pressure = Gauge("PRESSURE",    tag="pressure",    min_val=0, max_val=10,  units="bar")
        self.gauge_temp     = Gauge("TEMPERATURE", tag="temperature", min_val=0, max_val=150, units="°C")
        self.gauge_flow     = Gauge("FLOW RATE",   tag="flow_rate",   min_val=0, max_val=500, units="L/min")
        self.gauge_pressure.setFixedSize(140, 140)
        self.gauge_temp.setFixedSize(140, 140)
        self.gauge_flow.setFixedSize(140, 140)

        grid_layout.addWidget(self._wrap(self.tank_a),          0, 0)
        grid_layout.addWidget(self._wrap(self.pump_1),          0, 1)
        grid_layout.addWidget(self._wrap(self.pump_2),          0, 2)
        grid_layout.addWidget(self._wrap(self.tank_b),          0, 3)
        grid_layout.addWidget(self._wrap(self.gauge_pressure),  0, 4)
        grid_layout.addWidget(self._wrap(self.valve_in),        1, 0)
        grid_layout.addWidget(self._wrap(self.valve_out),       1, 1)
        grid_layout.addWidget(self._wrap(self.gauge_temp),      1, 2)
        grid_layout.addWidget(self._wrap(self.gauge_flow),      1, 3)

        root.addWidget(grid_box)

        if role_manager.has_permission("can_override"):
            root.addWidget(self._build_override_panel())

        root.addStretch()

    def _wrap(self, widget: QWidget) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet("QFrame { border: 1px solid #0f3460; border-radius: 6px; }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)
        return frame

    def _build_override_panel(self) -> QGroupBox:
        box = QGroupBox("Manual Override Controls")
        outer = QVBoxLayout(box)
        outer.setSpacing(12)

        # --- Row 1: Tank sliders ---
        tank_row = QHBoxLayout()
        tank_row.setSpacing(20)

        for label, tag, attr in [
            ("Tank A Level",    "tank_a_level", "slider_tank_a"),
            ("Tank B Level",    "tank_b_level", "slider_tank_b"),
            ("Pressure (bar)",  "pressure",     "slider_pressure"),
            ("Temperature (°C)","temperature",  "slider_temp"),
            ("Flow Rate",       "flow_rate",    "slider_flow"),
        ]:
            col = QVBoxLayout()
            col.addWidget(QLabel(label))
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(50)
            if tag == "tank_a_level" or tag == "tank_b_level":
                slider.valueChanged.connect(lambda v, t=tag: (self._sim_timer.stop(), tag_engine.set_tag(t, v / 100)))
            elif tag == "pressure":
                slider.valueChanged.connect(lambda v: (self._sim_timer.stop(), tag_engine.set_tag("pressure", v / 10)))
            elif tag == "temperature":
                slider.setValue(40)
                slider.valueChanged.connect(lambda v: (self._sim_timer.stop(), tag_engine.set_tag("temperature", v + 60)))
            elif tag == "flow_rate":
                slider.valueChanged.connect(lambda v: (self._sim_timer.stop(), tag_engine.set_tag("flow_rate", v * 5)))
            setattr(self, attr, slider)
            col.addWidget(slider)
            tank_row.addLayout(col)

        outer.addLayout(tank_row)

        # --- Row 2: Pump and valve toggles ---
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(12)

        self.btn_pump1 = QPushButton("START PUMP 1")
        self.btn_pump1.setCheckable(True)
        self.btn_pump1.toggled.connect(self._toggle_pump1)

        self.btn_pump2 = QPushButton("START PUMP 2")
        self.btn_pump2.setCheckable(True)
        self.btn_pump2.toggled.connect(self._toggle_pump2)

        self.btn_valve_in = QPushButton("OPEN INLET")
        self.btn_valve_in.setCheckable(True)
        self.btn_valve_in.toggled.connect(self._toggle_valve_in)

        self.btn_valve_out = QPushButton("OPEN OUTLET")
        self.btn_valve_out.setCheckable(True)
        self.btn_valve_out.toggled.connect(self._toggle_valve_out)

        for btn in [self.btn_pump1, self.btn_pump2,
                    self.btn_valve_in, self.btn_valve_out]:
            toggle_row.addWidget(btn)

        outer.addLayout(toggle_row)
        return box

    def _toggle_pump1(self, checked: bool):
        self._sim_timer.stop()  # stop demo when user takes control
        tag_engine.set_tag("pump_1_running", checked)
        self.btn_pump1.setText("STOP PUMP 1" if checked else "START PUMP 1")

    def _toggle_pump2(self, checked: bool):
        self._sim_timer.stop()
        tag_engine.set_tag("pump_2_running", checked)
        self.btn_pump2.setText("STOP PUMP 2" if checked else "START PUMP 2")

    def _toggle_valve_in(self, checked: bool):
        self._sim_timer.stop()
        tag_engine.set_tag("valve_inlet", 1.0 if checked else 0.0)
        self.btn_valve_in.setText("CLOSE INLET" if checked else "OPEN INLET")

    def _toggle_valve_out(self, checked: bool):
        self._sim_timer.stop()
        tag_engine.set_tag("valve_outlet", 1.0 if checked else 0.0)
        self.btn_valve_out.setText("CLOSE OUTLET" if checked else "OPEN OUTLET")

    def _bind_components(self):
        for comp in [self.tank_a, self.tank_b, self.pump_1, self.pump_2,
                     self.valve_in, self.valve_out,
                     self.gauge_pressure, self.gauge_temp, self.gauge_flow]:
            comp.bind(tag_engine)

    def _start_demo_simulation(self):
        self._sim_step = 0

        def tick():
            s = self._sim_step
            tag_engine.set_tag("tank_a_level",   0.5 + 0.35 * math.sin(s * 0.05))
            tag_engine.set_tag("tank_b_level",   0.3 + 0.25 * math.cos(s * 0.04))
            tag_engine.set_tag("pressure",       3.0 + 4.0  * abs(math.sin(s * 0.03)))
            tag_engine.set_tag("temperature",    60  + 40   * abs(math.sin(s * 0.02)))
            tag_engine.set_tag("flow_rate",      200 + 150  * abs(math.cos(s * 0.06)))
            tag_engine.set_tag("valve_outlet",   0.5 + 0.5  * math.sin(s * 0.07))
            tag_engine.set_tag("pump_2_running", (s // 30) % 2 == 0)
            self._sim_step += 1

        self._sim_timer = QTimer(self)
        self._sim_timer.timeout.connect(tick)
        self._sim_timer.start(200)
        tick()

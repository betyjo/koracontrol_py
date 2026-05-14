from PyQt6.QtCore import QObject, pyqtSignal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AlarmSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MEDIUM   = "MEDIUM"
    LOW      = "LOW"


class AlarmState(Enum):
    ACTIVE       = "ACTIVE"
    ACKNOWLEDGED = "ACK"
    CLEARED      = "CLEARED"


@dataclass
class Alarm:
    id: int
    tag: str
    message: str
    severity: AlarmSeverity
    state: AlarmState = AlarmState.ACTIVE
    timestamp: datetime = field(default_factory=datetime.now)
    ack_time: datetime | None = None
    ack_by: str | None = None

    def to_row(self) -> list:
        return [
            self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            self.severity.value,
            self.tag,
            self.message,
            self.state.value,
            self.ack_by or "",
        ]


class AlarmManager(QObject):
    alarm_raised   = pyqtSignal(object)
    alarm_acked    = pyqtSignal(object)
    alarm_cleared  = pyqtSignal(object)
    alarms_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._alarms: list[Alarm] = []
        self._next_id = 1

    def raise_alarm(self, tag: str, message: str,
                    severity: AlarmSeverity = AlarmSeverity.HIGH) -> Alarm:
        for a in self._alarms:
            if a.tag == tag and a.message == message and a.state == AlarmState.ACTIVE:
                return a
        alarm = Alarm(id=self._next_id, tag=tag, message=message, severity=severity)
        self._next_id += 1
        self._alarms.append(alarm)
        self.alarm_raised.emit(alarm)
        self.alarms_changed.emit()
        return alarm

    def acknowledge(self, alarm_id: int, user: str):
        for a in self._alarms:
            if a.id == alarm_id and a.state == AlarmState.ACTIVE:
                a.state = AlarmState.ACKNOWLEDGED
                a.ack_time = datetime.now()
                a.ack_by = user
                self.alarm_acked.emit(a)
                self.alarms_changed.emit()
                break

    def acknowledge_all(self, user: str):
        for a in self._alarms:
            if a.state == AlarmState.ACTIVE:
                a.state = AlarmState.ACKNOWLEDGED
                a.ack_time = datetime.now()
                a.ack_by = user
        self.alarms_changed.emit()

    def clear(self, alarm_id: int):
        for a in self._alarms:
            if a.id == alarm_id:
                a.state = AlarmState.CLEARED
                self.alarm_cleared.emit(a)
                self.alarms_changed.emit()
                break

    def active_alarms(self) -> list[Alarm]:
        return [a for a in self._alarms if a.state == AlarmState.ACTIVE]

    def all_alarms(self) -> list[Alarm]:
        return list(reversed(self._alarms))

    def active_count(self) -> int:
        return len(self.active_alarms())


alarm_manager = AlarmManager()

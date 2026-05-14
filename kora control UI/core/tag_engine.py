from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TagEngine(QObject):
    tag_updated = pyqtSignal(str, object)

    def __init__(self, refresh_ms: int = 200, parent=None):
        super().__init__(parent)
        self._tags: dict[str, object] = {}
        self._refresh_ms = refresh_ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)

    def start(self):
        self._timer.start(self._refresh_ms)

    def stop(self):
        self._timer.stop()

    def set_tag(self, name: str, value: object):
        self._tags[name] = value
        self.tag_updated.emit(name, value)

    def get_tag(self, name: str, default=None):
        return self._tags.get(name, default)

    def _poll(self):
        # Replace this with your real Industrial Communication API calls:
        # values = comm_api.read_all_tags()
        # for name, value in values.items():
        #     if self._tags.get(name) != value:
        #         self._tags[name] = value
        #         self.tag_updated.emit(name, value)
        pass


tag_engine = TagEngine(refresh_ms=200)

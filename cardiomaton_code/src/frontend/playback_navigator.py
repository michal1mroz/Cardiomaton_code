from PyQt6.QtCore import QTimer, QObject, pyqtSignal

class PlaybackNavigator(QObject):
    request_render_buffer = pyqtSignal(int)
    interaction_started = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.frames_per_click = 10
        self.current_buffer_index = -1

        self._playback_timer = QTimer()
        self._playback_timer.timeout.connect(self._step_backward)

        self._forward_timer = QTimer()
        self._forward_timer.timeout.connect(self._step_forward)

        self._sim_buffer_size = 0

    def set_buffer_size(self, size: int):
        self._sim_buffer_size = size

    def reset_index(self):
        self.current_buffer_index = -1

    def start_backward_hold(self):
        self._step_backward()
        self._playback_timer.start(100)

    def stop_backward_hold(self):
        self._playback_timer.stop()

    def start_forward_hold(self):
        self._step_forward()
        self._forward_timer.start(100)

    def stop_forward_hold(self):
        self._forward_timer.stop()

    def _step_backward(self):
        self.interaction_started.emit()
        new_index = self.current_buffer_index - self.frames_per_click
        if new_index < -self._sim_buffer_size:
            new_index = -self._sim_buffer_size
        self._update_index(new_index)

    def _step_forward(self):
        self.interaction_started.emit()
        new_index = self.current_buffer_index + self.frames_per_click
        if new_index > -1:
            new_index = -1
        self._update_index(new_index)

    def _update_index(self, index):
        self.current_buffer_index = index
        self.request_render_buffer.emit(index)
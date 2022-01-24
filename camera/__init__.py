import threading


class Camera:
    def __init__(self):
        self.sequence_running = False
        self.sequence_counter = 0
        self.sequence_length = 0
        self.sequence_pause = 0
        self.images = []

    def connect(self):
        pass

    def disconnect(self):
        pass

    def capture_image(self):
        pass

    def start_sequence(self, length, pause):
        if not self.sequence_running:
            self.sequence_counter = 0
            self.sequence_length = length
            self.sequence_pause = pause
            self.sequence_running = True
            threading.Thread(target=self._start_sequence).start()

    def stop_sequence(self):
        if self.sequence_running:
            self.sequence_running = False

    def _start_sequence(self):
        while self.sequence_counter < self.sequence_length and self.sequence_running:
            self.images.append(self.capture_image())
            time.sleep(self.sequence_pause)
        if not self.sequence_running:
            self.sequence_running = False

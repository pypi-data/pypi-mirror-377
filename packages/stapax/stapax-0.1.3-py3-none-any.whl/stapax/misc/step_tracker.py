from multiprocessing import RLock

# TODO: make this work with multiple GPU training


class StepTracker:
    lock: RLock
    step: int

    def __init__(self):
        self.lock = RLock()
        self.step = 0

    def set_step(self, step: int) -> None:
        with self.lock:
            self.step = step

    def get_step(self) -> int:
        with self.lock:
            return self.step

import threading
import time

class GitHubTimer:
    def __init__(self, syncer, interval_minutes):
        self.syncer = syncer
        self.interval = max(1, interval_minutes) * 60
        self.timer = None
        self.is_active = False
        self._lock = threading.RLock()
    
    def start(self):
        with self._lock:
            if not self.is_active:
                self.is_active = True
                self._schedule_sync()
    
    def stop(self):
        with self._lock:
            if self.timer:
                self.timer.cancel()
            self.is_active = False
    
    def _schedule_sync(self):
        with self._lock:
            if self.is_active:
                self.timer = threading.Timer(self.interval, self._sync_and_reschedule)
                self.timer.daemon = True
                self.timer.start()
    
    def _sync_and_reschedule(self):
        try:
            self.syncer.sync_if_changed()
        except Exception as e:
            print(f"GitHub sync error: {e}")
        self._schedule_sync()
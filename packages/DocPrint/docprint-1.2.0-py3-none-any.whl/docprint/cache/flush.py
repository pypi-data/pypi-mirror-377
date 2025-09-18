import threading
from ..config.constants import CACHE_FLUSH_INTERVAL

class FlushController:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.timer = None
        self.is_active = False
        self._lock = threading.RLock()
    
    def start_timer(self):
        with self._lock:
            if not self.is_active:
                self.is_active = True
                self._schedule_flush()
    
    def stop_timer(self):
        with self._lock:
            if self.timer:
                self.timer.cancel()
            self.is_active = False
    
    def _schedule_flush(self):
        with self._lock:
            if self.is_active:
                self.timer = threading.Timer(CACHE_FLUSH_INTERVAL, self._flush_and_reschedule)
                self.timer.daemon = True
                self.timer.start()
    
    def _flush_and_reschedule(self):
        with self._lock:
            if self.cache_manager:
                self.cache_manager.flush()
        self._schedule_flush()
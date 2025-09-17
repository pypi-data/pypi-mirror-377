import time
from ..config.constants import CACHE_FLUSH_INTERVAL, CACHE_FLUSH_COUNT
from ..files.handler import FileHandler

try:
    import xxhash
    def _hash_content(content):
        return xxhash.xxh64(content.encode('utf-8')).hexdigest()
except ImportError:
    import hashlib
    def _hash_content(content):
        return hashlib.md5(content.encode('utf-8')).hexdigest()

class CacheManager:
    def __init__(self):
        self.cache = []
        self.content_hashes = {}
        self.last_flush_time = time.time()
        self.call_count = 0
        self.file_handler = FileHandler()
        self.flush_controller = None
    
    def add_entry(self, header, content):
        content_hash = _hash_content(content)

        if header in self.content_hashes:
            if self.content_hashes[header] == content_hash:
                return

        self.content_hashes[header] = content_hash
        self.cache.append({
            'header': header,
            'content': content,
            'timestamp': time.time()
        })
        self.call_count += 1
        
        if self.flush_controller is None:
            self._initialize_flush_controller()
        
        self._check_flush_conditions()
    
    def _check_flush_conditions(self):
        time_elapsed = time.time() - self.last_flush_time
        if (time_elapsed >= CACHE_FLUSH_INTERVAL or 
            self.call_count >= CACHE_FLUSH_COUNT):
            self.flush()
    
    def flush(self):
        if not self.cache:
            return
        
        self.file_handler.write_cached_content(self.cache)
        self.cache.clear()
        self.call_count = 0
        self.last_flush_time = time.time()
    
    def _initialize_flush_controller(self):
        from .flush import FlushController
        self.flush_controller = FlushController(self)
        self.flush_controller.start_timer()
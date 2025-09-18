import time
from ..config.constants import CACHE_FLUSH_INTERVAL, CACHE_FLUSH_COUNT
from ..files.handler import FileHandler
from ..content.layout_utils import LayoutUtils

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
        self.header_cache = set()
        self.last_flush_time = time.time()
        self.call_count = 0
        self.file_handler = FileHandler()
        self.flush_controller = None
    
    def _ensure_unique_header(self, original_header):
        if original_header not in self.header_cache:
            return original_header
        
        counter = 1
        while f"{original_header} ({counter})" in self.header_cache:
            counter += 1
        
        return f"{original_header} ({counter})"
    
    def add_entry(self, header, content):
        unique_header = self._ensure_unique_header(header)
        self.header_cache.add(unique_header)
        
        updated_content = content.replace(f"## {header}", f"## {unique_header}", 1) if header != unique_header else content
        
        if LayoutUtils.is_layout_content(updated_content):
            normalized_content = LayoutUtils.normalize_layout_content(updated_content)
            content_hash = _hash_content(normalized_content)
        else:
            content_hash = _hash_content(updated_content)

        self.content_hashes[unique_header] = content_hash
        self.cache.append({
            'header': unique_header,
            'content': updated_content,
            'timestamp': time.time()
        })
        self.call_count += 1
        
        if self.flush_controller is None:
            self._initialize_flush_controller()
        
        self._check_flush_conditions()
        return unique_header
    
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
    
    def clear_header_cache(self):
        self.header_cache.clear()
    
    def _initialize_flush_controller(self):
        from .flush import FlushController
        self.flush_controller = FlushController(self)
        self.flush_controller.start_timer()
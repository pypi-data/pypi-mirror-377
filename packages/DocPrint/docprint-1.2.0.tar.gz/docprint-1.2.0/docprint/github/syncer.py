import base64
import urllib.request
import urllib.error
from .auth import GitHubAuth, dumps, loads
from .timer import GitHubTimer

try:
    import xxhash
    def _hash_file_content(content):
        return xxhash.xxh64(content.encode('utf-8')).hexdigest()
except ImportError:
    import hashlib
    def _hash_file_content(content):
        return hashlib.md5(content.encode('utf-8')).hexdigest()

class GitHubSyncer:
    def __init__(self, token, repo, file_handler):
        self.auth = GitHubAuth(token, repo)
        self.file_handler = file_handler
        self.timer = None
        self.last_synced_hash = None
        self.is_enabled = False
    
    def enable(self, interval_minutes=1):
        if not self.auth.validate_repo_access():
            raise ValueError(f"Cannot access repository: {self.auth.repo}")
        
        self.is_enabled = True
        self.timer = GitHubTimer(self, interval_minutes)
        self.timer.start()
    
    def disable(self):
        self.is_enabled = False
        if self.timer:
            self.timer.stop()
    
    def sync_if_changed(self):
        if not self.is_enabled:
            return
        
        current_content = self._get_current_file_content()
        if not current_content:
            return
        
        current_hash = _hash_file_content(current_content)
        if current_hash == self.last_synced_hash:
            return
        
        if self._push_to_github(current_content):
            self.last_synced_hash = current_hash
    
    def _get_current_file_content(self):
        try:
            if self.file_handler.target_file.exists():
                return self.file_handler.target_file.read_text(encoding='utf-8')
        except Exception:
            pass
        return ""
    
    def _push_to_github(self, content):
        try:
            file_path = self.file_handler.current_filename or "DOC.PRINT.md"
            
            sha = self._get_file_sha(file_path)
            
            data = {
                'message': f'DocPrint: update {file_path}',
                'content': base64.b64encode(content.encode('utf-8')).decode('utf-8')
            }
            
            if sha:
                data['sha'] = sha
            
            url = f'https://api.github.com/repos/{self.auth.repo}/contents/{file_path}'
            req = urllib.request.Request(
                url, 
                data=dumps(data).encode('utf-8'), 
                headers=self.auth.headers,
                method='PUT'
            )
            
            urllib.request.urlopen(req)
            return True
            
        except Exception as e:
            print(f"GitHub push failed: {e}")
            return False
    
    def _get_file_sha(self, file_path):
        try:
            url = f'https://api.github.com/repos/{self.auth.repo}/contents/{file_path}'
            req = urllib.request.Request(url, headers=self.auth.headers)
            response = urllib.request.urlopen(req)
            data = loads(response.read().decode('utf-8'))
            return data.get('sha')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
import urllib.request
import urllib.error

try:
    import orjson as json
    def dumps(data):
        return json.dumps(data).decode('utf-8')
    def loads(data):
        return json.loads(data)
except ImportError:
    try:
        import ujson as json
        dumps = json.dumps
        loads = json.loads
    except ImportError:
        import json
        dumps = json.dumps
        loads = json.loads

class GitHubAuth:
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
    
    def validate_repo_access(self):
        url = f'https://api.github.com/repos/{self.repo}'
        try:
            req = urllib.request.Request(url, headers=self.headers)
            urllib.request.urlopen(req)
            return True
        except urllib.error.HTTPError:
            return False
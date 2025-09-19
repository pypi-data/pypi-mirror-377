import json
from urllib.parse import urlparse, parse_qs

class Request:
    def __init__(self, handler, route_match=None):
        self.path = handler.path
        self.method = handler.command
        self.headers = handler.headers
        self.query = {}
        self.body = None
        self.params = {}
        self.raw_handler = handler

        content_length = handler.headers.get("Content-Length")
        if content_length:
            length = int(content_length)
            self.body = handler.rfile.read(length).decode()
            try:
                self.json = json.loads(self.body)
            except:
                self.json = None
        else:
            self.json = None

        parsed = urlparse(self.path)
        self.query = {k: v[0] if len(v)==1 else v for k, v in parse_qs(parsed.query).items()}

        if route_match:
            self.params = route_match

class Response:
    def __init__(self, handler):
        self.handler = handler
        self.status_code = 200
        self.headers = {"Content-Type": "text/plain"}
        self._body = b''

    def json(self, data):
        self.headers["Content-Type"] = "application/json"
        self._body = json.dumps(data).encode()
        self.send()

    def html(self, data):
        self.headers["Content-Type"] = "text/html"
        self._body = data.encode()
        self.send()

    def send(self, data=None):
        if data:
            self._body = data.encode() if isinstance(data, str) else data
        self.handler.send_response(self.status_code)
        for k, v in self.headers.items():
            self.handler.send_header(k, v)
        self.handler.end_headers()
        self.handler.wfile.write(self._body)

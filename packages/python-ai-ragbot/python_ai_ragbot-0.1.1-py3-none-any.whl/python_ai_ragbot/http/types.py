import json

class PortableRequest:
    def __init__(self, method, url, headers, query, body, audio_bytes, raw):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.query = query or {}
        self.body = body or {}
        self.audio_bytes = audio_bytes
        self.raw = raw

class ResponseWriter:
    def __init__(self, res_like):
        self.res_like = res_like

    def json(self, status, payload, headers=None):
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
        body = json.dumps(payload).encode("utf-8")

        # res_like supports: (status_code, headers list, body iterable) – WSGI style
        # or has set_status/headers/body patterns (FastAPI/Flask adapters will adapt)
        return status, headers, body

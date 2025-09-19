import re

class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, path, methods, handler, controller, guards=None, middlewares=None):
        regex_path = re.sub(r':(\w+)', lambda m: f"(?P<{m.group(1)}>[^/]+)", path)
        regex = re.compile(f"^{regex_path}$")
        self.routes.append({
            "regex": regex,
            "methods": [m.upper() for m in methods],
            "handler": handler,
            "controller": controller,
            "guards": guards or [],
            "middlewares": middlewares or []
        })

    def match(self, path, method):
        for route in self.routes:
            if method.upper() not in route["methods"]:
                continue
            m = route["regex"].match(path)
            if m:
                return route, m.groupdict()
        return None, None

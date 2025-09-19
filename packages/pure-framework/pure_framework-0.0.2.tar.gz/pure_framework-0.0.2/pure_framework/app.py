from http.server import BaseHTTPRequestHandler, HTTPServer
from .decorators import ROUTES
from .router import Router
from .http import Request, Response
from .pipeline import run_middlewares, run_guards
from .utils import inject_params
from .swagger import generate_openapi
import json
from typing import cast

# Subclass HTTPServer to make `app` a known attribute for Pylance/IDE
class AppHTTPServer(HTTPServer):
    app: "App"

class App:
    def __init__(self):
        self._router = Router()
        self._middlewares = []

    def use(self, mw):
        """Register a global middleware"""
        self._middlewares.append(mw)

    def register_routes(self):
        """Register all controllers and nested routes"""
        def register_cls(cls, parent_prefix=""):
            prefix = getattr(cls, "_prefix", "")
            for attr_name in dir(cls):
                attr = getattr(cls, attr_name)
                if hasattr(attr, "_routes"):
                    for route in attr._routes:
                        path = parent_prefix + prefix + route["path"]
                        self._router.add_route(
                            path,
                            route["methods"],
                            route["handler"],
                            cls,
                            route.get("guards"),
                            route.get("middlewares")
                        )
            for child_cls in getattr(cls, "_child_controllers", []):
                register_cls(child_cls, parent_prefix + prefix)

        top_controllers = list({r["controller"] for r in ROUTES})
        for cls in top_controllers:
            register_cls(cls)

    def serve_swagger(self):
        """Serve Swagger UI dynamically"""
        openapi_json = generate_openapi()
        openapi_str = json.dumps(openapi_json)
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <title>Swagger UI</title>
          <link href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.18.3/swagger-ui.css" rel="stylesheet">
        </head>
        <body>
          <div id="swagger-ui"></div>
          <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.18.3/swagger-ui-bundle.js"></script>
          <script>
            const spec = {openapi_str};
            SwaggerUIBundle({{ spec, dom_id: '#swagger-ui' }});
          </script>
        </body>
        </html>
        """

    def listen(self, host="127.0.0.1", port=8000):
        """Start the HTTP server"""
        self.register_routes()
        app_middlewares = self._middlewares

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self): self.handle_request("GET")
            def do_POST(self): self.handle_request("POST")

            def handle_request(self, method):
                # Tell type checker that self.server is AppHTTPServer
                server: AppHTTPServer = cast(AppHTTPServer, self.server)
                path = self.path.split('?')[0]
                req = Request(self, route_match=None)
                res = Response(self)

                if path == "/docs":
                    res.html(server.app.serve_swagger())
                    return

                # Global middlewares
                run_middlewares(app_middlewares, req, res)

                # Match route
                route, params = server.app._router.match(path, method)
                if route:
                    req.params = params
                    if not run_guards(route.get("guards", []), req, res):
                        return
                    run_middlewares(route.get("middlewares", []), req, res)

                    ctrl = route["controller"]()
                    try:
                        kwargs = inject_params(route["handler"], req)
                    except ValueError as e:
                        res.status_code = 400
                        res.json({"error": str(e)})
                        return

                    route["handler"](ctrl, **kwargs, req=req, res=res)
                    return

                res.status_code = 404
                res.send("Not Found")

        # Use subclassed server to satisfy Pylance
        server = AppHTTPServer((host, port), Handler)
        server.app = self
        print(f"Server running at http://{host}:{port} (Swagger docs: /docs)")
        server.serve_forever()

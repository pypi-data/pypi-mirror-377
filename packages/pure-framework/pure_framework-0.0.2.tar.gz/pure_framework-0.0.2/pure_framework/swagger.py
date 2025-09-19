from .decorators import ROUTES
import inspect

def generate_openapi(title="API", version="1.0.0"):
    paths = {}
    for route in ROUTES:
        path = route['path']
        method = route['methods'][0].lower()
        if path not in paths:
            paths[path] = {}
        handler = route['handler']
        sig = inspect.signature(handler)
        parameters = []
        for name, param in sig.parameters.items():
            if name in ('self', 'req', 'res'):
                continue
            param_info = {
                "name": name,
                "in": "query" if param.default != param.empty else "path",
                "required": param.default == param.empty,
                "schema": {"type": param.annotation.__name__ if param.annotation != param.empty else "string"}
            }
            parameters.append(param_info)
        paths[path][method] = {
            "summary": handler.__name__,
            "parameters": parameters,
            "responses": {"200": {"description": "Success"}}
        }
    openapi = {"openapi": "3.0.0", "info": {"title": title, "version": version}, "paths": paths}
    return openapi

import inspect

ROUTES = []

def controller(prefix="", children=None):
    children = children or []
    def decorator(cls):
        cls._prefix = prefix
        cls._child_controllers = children

        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, "_routes"):
                for route_info in attr._routes:
                    route_info_copy = route_info.copy()
                    route_info_copy['path'] = prefix + route_info_copy['path']
                    route_info_copy['controller'] = cls
                    ROUTES.append(route_info_copy)
        return cls
    return decorator

def route(path, methods=["GET"], guards=None, middlewares=None):
    guards = guards or []
    middlewares = middlewares or []

    def decorator(func):
        if not hasattr(func, "_routes"):
            func._routes = []
        func._routes.append({
            "path": path,
            "methods": [m.upper() for m in methods],
            "guards": guards,
            "middlewares": middlewares,
            "handler": func
        })
        return func
    return decorator

def get(path, **kwargs): return route(path, methods=["GET"], **kwargs)
def post(path, **kwargs): return route(path, methods=["POST"], **kwargs)
def put(path, **kwargs): return route(path, methods=["PUT"], **kwargs)
def delete(path, **kwargs): return route(path, methods=["DELETE"], **kwargs)

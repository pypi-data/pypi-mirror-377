def run_middlewares(middlewares, req, res):
    for mw in middlewares:
        mw(req, res)

def run_guards(guards, req, res):
    for guard in guards:
        if not guard(req):
            res.status_code = 403
            res.send("Forbidden")
            return False
    return True

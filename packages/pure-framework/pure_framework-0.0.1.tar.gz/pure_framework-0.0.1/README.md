# Pure Framework

Pure Python backend framework inspired by NestJS & FastAPI.  
- No external dependencies
- Decorator-based routing
- Nested controllers
- Middleware & Guards
- Swagger documentation

## Installation

```bash
pip install pure-framework
````

## Quick Start

```python
from pure_framework import App, Request, Response, route

app = App()

@route("/hello")
def hello(req: Request, res: Response):
    res.json({"message": "Hello World"})

app.listen(host="127.0.0.1", port=8000)
```

Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to see Swagger docs.

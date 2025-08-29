from infrastructure.web.app import app as asgi_app
from a2wsgi import ASGIMiddleware

app = ASGIMiddleware(asgi_app)

from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware

from . import templating, paths


def create():
    return Cuddy()


class IndexController(object):
    def __init__(self, models):
        self._models = models


class Cuddy(object):
    def __init__(self):
        self._models = []
        self._templates = templating.templates()
    
    def add(self, model):
        self._models.append(model)
    
    def respond(self, request):
        return Response(
            self._templates.template("index.html", {"models": self._models}),
            mimetype="text/html",
        )

    def wsgi_app(self):
        def handle(environ, start_response):
            request = Request(environ)
            response = self.respond(request)
            response = SharedDataMiddleware(response, {
                "/static": paths.local_project_path("static"),
            })
            return response(environ, start_response)
            
        return handle

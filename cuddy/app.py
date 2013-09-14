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
        path_parts = filter(lambda part: part, request.path.split("/"))
        if len(path_parts) == 1:
            model_slug = path_parts[0]
            ModelAdmin = next(model for model in self._models if model.slug == model_slug)
            model_admin = ModelAdmin()
            
            instances = [
                {"fields": [field.read(instance) for field in model_admin.index_fields()]}
                for instance in model_admin.fetch_all()
            ]
            
            return Response(
                self._templates.template("model-index.html", {"fields": model_admin.fields, "instances": instances}),
                mimetype="text/html",
            )
        else:
            model_view_models = [
                # TODO: reverse URLs
                ModelViewModel(model.name, "/{0}".format(model.slug))
                for model in self._models
            ]
            
            return Response(
                self._templates.template("index.html", {"models": model_view_models}),
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


class ModelViewModel(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

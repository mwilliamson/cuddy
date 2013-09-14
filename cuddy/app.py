from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware
import zuice

from . import templating, paths


def create():
    return Cuddy()


class IndexController(zuice.Base):
    _model_admins = zuice.dependency("model-admins")
    _templates = zuice.dependency(templating.Templates)
    
    def respond(self, request):
        model_view_models = [
            # TODO: reverse URLs
            ModelViewModel(model.name, "/{0}".format(model.slug))
            for model in self._model_admins
        ]
        
        return Response(
            self._templates.template("index.html", {"models": model_view_models}),
            mimetype="text/html",
        )


class ModelIndexController(zuice.Base):
    _model_admins = zuice.dependency("model-admins")
    _templates = zuice.dependency(templating.Templates)
    
    def respond(self, request, model_slug):
        ModelAdmin = next(model for model in self._model_admins if model.slug == model_slug)
        model_admin = ModelAdmin()
        
        instances = [
            {"fields": [field.read(instance) for field in model_admin.index_fields()]}
            for instance in model_admin.fetch_all()
        ]
        
        return Response(
            self._templates.template("model-index.html", {"fields": model_admin.fields, "instances": instances}),
            mimetype="text/html",
        )
    

class Cuddy(object):
    def __init__(self):
        self._models = []
    
    def add(self, model):
        self._models.append(model)
    
    def respond(self, request):
        bindings = zuice.Bindings()
        bindings.bind("model-admins").to_instance(self._models)
        bindings.bind(templating.Templates).to_instance(templating.templates())
        
        injector = zuice.Injector(bindings)
        path_parts = filter(lambda part: part, request.path.split("/"))
        
        if len(path_parts) == 1:
            controller_cls = ModelIndexController
        else:
            controller_cls = IndexController
            
        controller = injector.get(controller_cls)
        return controller.respond(request, *path_parts)

    def wsgi_app(self):
        def handle(environ, start_response):
            request = Request(environ)
            response = self.respond(request)
            return response(environ, start_response)
            
        return SharedDataMiddleware(handle, {
            "/static": paths.local_project_path("static"),
        })


class ModelViewModel(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

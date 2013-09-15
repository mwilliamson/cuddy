from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware
import zuice

from . import templating, paths


def create():
    return Cuddy()


# TODO: reverse URLs
def url_model_index(model_admin):
    return"/{0}".format(model_admin.slug)
    
    
def url_model_instance(model_admin, instance):
    return "/{0}/{1}".format(model_admin.slug, model_admin.identify(instance))


class IndexController(zuice.Base):
    _model_admins = zuice.dependency("model-admins")
    _templates = zuice.dependency(templating.Templates)
    
    def respond(self, request):
        model_view_models = [
            ModelViewModel(model.name, url_model_index(model))
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
        model_admin = next(model for model in self._model_admins if model.slug == model_slug)
        
        fields = model_admin.fields
        
        instances = [
            {
                "fields": [
                    {
                        "title": field.title,
                        "value": field.short_describe(instance),
                    }
                    for field in fields
                ],
                "url": url_model_instance(model_admin, instance),
            }
            for instance in model_admin.fetch_all()
        ]
        
        context = {
            "fields": fields,
            "instances": instances,
            "edit_link_field": model_admin.edit_link_field,
        }
        
        return Response(
            self._templates.template("model-index.html", context),
            mimetype="text/html",
        )


class ModelInstanceController(zuice.Base):
    _model_admins = zuice.dependency("model-admins")
    _templates = zuice.dependency(templating.Templates)
    
    def respond(self, request, model_slug, instance_id):
        model_admin = next(model for model in self._model_admins if model.slug == model_slug)
        
        instance = model_admin.fetch_by_id(instance_id)
        context = {
            "title": model_admin.short_describe(instance),
            "fields": [
                {
                    "title": field.title,
                    "slug": field.slug,
                    "editor": field.editor(instance),
                }
                for field in model_admin.fields
            ]
        }
        
        return Response(
            self._templates.template("model-instance.html", context),
            mimetype="text/html",
        )

    
    

class Cuddy(object):
    def __init__(self):
        self._models = []
    
    def add(self, model):
        self._models.append(model)
    
    def respond(self, request):
        bindings = zuice.Bindings()
        bindings.bind("model-admins").to_provider(lambda injector: map(injector.get, self._models))
        bindings.bind(templating.Templates).to_instance(templating.templates())
        
        injector = zuice.Injector(bindings)
        path_parts = filter(lambda part: part, request.path.split("/"))
        
        if len(path_parts) == 1:
            controller_cls = ModelIndexController
        elif len(path_parts) == 2:
            controller_cls = ModelInstanceController
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

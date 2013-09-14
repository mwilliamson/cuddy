import os

import jinja2

from . import paths


def templates():
    template_root = paths.local_project_path("templates")
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_root),
        autoescape=True
    )
    return Templates(jinja_env)
    


class Templates(object):
    def __init__(self, jinja_env):
        self._jinja_env = jinja_env
        
    def template(self, name, context=None):
        template = self._jinja_env.get_template(name)
        return template.render(context)

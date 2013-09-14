import os


def local_project_path(path):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(os.path.dirname(this_dir), path)

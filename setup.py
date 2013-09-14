#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='cuddy',
    version='0.1.0',
    description='Declaratively build an administrative interface',
    long_description=read("README"),
    author='Michael Williamson',
    url='http://github.com/mwilliamson/cuddy.py',
    packages=['cuddy'],
    install_requires=[
        "werkzeug>=0.9.4,<0.10",
        "jinja2>=2.7.1,<2.8",
        "zuice>=0.2,<0.3",
    ],
)

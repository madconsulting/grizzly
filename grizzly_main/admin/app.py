#!/usr/bin/env python

# standard lib
# import json
# import logging

# third party
from flask import Flask
from jinja2 import Environment, FileSystemLoader

jinja_file_loader = FileSystemLoader("./templates")
jinja_env = Environment(loader=jinja_file_loader, autoescape=True)

__version__ = "0.0.1"
app = Flask(__name__)


@app.route("/")
def index():
    template = jinja_env.get_template("index.html")
    output = template.render()
    return output, 200


@app.route("/version")
def version():
    return {"msg": f"{__version__}"}

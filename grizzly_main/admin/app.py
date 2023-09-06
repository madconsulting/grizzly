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
    """
    The above function renders the "index.html" template using Jinja and returns the rendered output
    with a status code of 200.
    :return: the rendered output of the "index.html" template and a status code of 200.
    """
    template = jinja_env.get_template("index.html")
    output = template.render()
    return output, 200


@app.route("/version")
def version():
    """
    The function returns the value of the `__version__` variable as a dictionary with a key "msg".
    :return: a dictionary with a key "msg" and a value that is the value of the "__version__" variable.
    """
    return {"msg": f"{__version__}"}

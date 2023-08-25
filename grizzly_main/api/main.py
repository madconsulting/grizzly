#!/usr/bin/env python

# standard lib
# import os

# third party
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

__version__ = "0.0.1"
app = FastAPI(title="Grizzly API")


@app.route("/")
def hello_grizzly():
    """
    The function `hello_grizzly` returns a JSON response with the message "hello grizzly_main" and a status code of 200.

    :return: a JSON response with the message "hello grizzly_main" and a status code of 200.
    """
    return JSONResponse({"msg": "hello grizzly_main"}, status_code=200)


@app.route("/docs")
def docs():
    """
    The function `docs()` returns the Swagger UI HTML code with specified parameters.
    :return: the Swagger UI HTML code.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Grizzly - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

#!/usr/bin/env python

# standard lib
import os

# third party
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html


__version__ = '0.0.1'
app = FastAPI(title="Grizzly API")


@app.route('/')
def hello_grizzly(root_path):
    return JSONResponse({'msg': 'hello grizzly'}, status_code=200)


@app.route('/docs')
def docs():
    return get_swagger_ui_html(
        openapi_url = app.openapi_url,
        title = "Grizzly - Swagger UI",
        oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url,
        swagger_js_url = "/static/swagger-ui-bundle.js",
        swagger_css_url = "/static/swagger-ui.css",
        )

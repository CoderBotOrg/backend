#!/usr/bin/python

import os
import logging
import logging.handlers
import connexion
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

# Logging configuration
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

## (Connexion) Flask app configuration

# Serve a custom version of the swagger ui (Jinja2 templates) based on the default one
#  from the folder 'swagger-ui'. Clone the 'swagger-ui' repository inside the backend folder

app = connexion.App(__name__)
app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## New API and web application

# API v1 is defined in v1.yml and its methods are in api.py
app.add_api('v1.yml')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
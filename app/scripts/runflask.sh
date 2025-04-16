#!/bin/bash
export FLASK_SECRET_KEY="$(openssl rand -base64 16)"
flask run --host=0.0.0.0
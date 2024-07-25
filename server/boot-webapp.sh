#!/bin/bash
source venv/bin/activate
flask db upgrade
exec flask run --host=0.0.0.0 --port=5000

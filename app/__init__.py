from flask import Flask, request, Response, stream_with_context, render_template, send_from_directory
from datetime import datetime
import paho.mqtt.client as mqtt
import time
from collections import defaultdict  # Import defaultdict
import os
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)#creates a flask application instance and assinges it to variable app, name is to figure out the path 
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes,models
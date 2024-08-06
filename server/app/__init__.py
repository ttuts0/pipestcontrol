from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
os.chmod(Config.UPLOAD_FOLDER, 0o755)

# Import routes and models after initializing Flask app and db
from app import routes, models
from cli import register_commands
register_commands(app)

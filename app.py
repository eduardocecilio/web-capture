import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scheduler.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Import routes after app creation to avoid circular imports
from routes import *

# Create database tables and initialize scheduler
with app.app_context():
    # Import models to register them
    import models
    db.create_all()
    
    # Initialize scheduler
    from scheduler import init_scheduler
    init_scheduler()

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

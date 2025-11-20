import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)

# Vercel-specific middleware
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Security
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure database
database_url = os.environ.get("POSTGRES_URL")
if database_url:
    # Vercel Postgres (production)
    logger.info("Usando Vercel Postgres")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # SQLite (desenvolvimento local)
    logger.info("Usando SQLite local")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///local.db"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Import routes after app creation to avoid circular imports
from routes import *  # noqa: F401, E402

# Create database tables
with app.app_context():
    # Import models to register them
    import models  # noqa: F401, E402
    db.create_all()
    logger.info("Database initialized")

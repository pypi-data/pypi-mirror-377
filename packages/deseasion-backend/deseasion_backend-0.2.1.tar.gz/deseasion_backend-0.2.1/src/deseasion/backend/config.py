DEBUG = False

PROPAGATE_EXCEPTIONS = True  # allow the app to handle exceptions

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = ""  # overwrite this option in `instance/config.py`
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Swagger configuration (for flasgger)
SWAGGER = {
    "title": "DESEASION API docs",
    "version": "2.1.1",
    "openapi": "3.0.2",
}
API_ROOT = "/api"

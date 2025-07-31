import os

from cachelib import FileSystemCache
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import URL
from flask_session import Session
from watcher import home
from watcher.db import db
from flask_wtf.csrf import CSRFProtect


def ignite() -> Flask:
    """Driver function to start the Watcher application

    Returns:
        Flask: Flask application with all attached routes and middleware
    """
    app = Flask(__name__)
    load_dotenv()
    app.config['SECRET_KEY'] = os.environ["WATCHER_SECRET"]
    
    csrf = CSRFProtect()
    connection_url = URL.create(
        "mssql+pyodbc",
        username=os.environ["WATCHER_DB_USERNAME"],
        password=os.environ["WATCHER_DB_PASSWORD"],
        host=os.environ["WATCHER_DB_HOST"],
        port=int(os.environ["WATCHER_DB_PORT"]),
        database=os.environ["WATCHER_DB_NAME"],
        query={
            "driver": f"ODBC Driver {os.environ["WATCHER_DB_DRIVER_VERSION"]} for SQL Server",
            "TrustServerCertificate": "yes",
        },
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = connection_url
    
    app.config["SESSION_TYPE"] = "cachelib"
    app.config["SESSION_SERIALIZATION_FORMAT"] = "json"
    app.config["SESSION_CACHELIB"] = FileSystemCache(threshold=500, cache_dir='./src/watcher/session')
    Session(app)

    csrf.init_app(app) # type: ignore
    db.init_app(app)

    app.register_blueprint(home.bp)

    return app

from flask import Flask
from sqlalchemy import URL
from watcher import home
from watcher.db import db
import os
from dotenv import load_dotenv
from urllib import parse


def ignite() -> Flask:
    """Driver function to start the Watcher application

    Returns:
        Flask: Flask application with all attached routes and middleware
    """
    app = Flask(__name__)
    load_dotenv()
    connection_url = URL.create(
        "mssql+pyodbc",
        username=os.environ["WATCHER_DB_USERNAME"],
        password=os.environ["WATCHER_DB_PASSWORD"],
        host=os.environ["WATCHER_DB_HOST"],
        port=int(os.environ["WATCHER_DB_PORT"]),
        database=os.environ["WATCHER_DB_NAME"],
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "TrustServerCertificate": "yes"
        },
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = connection_url
    
    db.init_app(app)
    
    app.register_blueprint(home.bp)
    
    return app

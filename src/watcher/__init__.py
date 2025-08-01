import os

from dotenv import load_dotenv
from flask import Flask
from flask_session import Session  # pyright: ignore[reportMissingTypeStubs]
from flask_wtf.csrf import CSRFProtect  # pyright: ignore[reportMissingTypeStubs]
from redis import Redis
from sqlalchemy import URL
from werkzeug.middleware.proxy_fix import ProxyFix

from watcher import home
from watcher.db import db


def ignite() -> Flask:
    """Driver function to start the Watcher application

    Returns:
        Flask: Flask application with all attached routes and middleware
    """
    app = Flask(__name__)
    load_dotenv("stack.env")
    app.config["SECRET_KEY"] = os.environ["WATCHER_SECRET"]

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

    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = Redis.from_url("redis://127.0.0.1:6379")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1, x_prefix=1)
    Session(app)

    csrf.init_app(app)  # type: ignore
    db.init_app(app)

    app.register_blueprint(home.bp)

    return app

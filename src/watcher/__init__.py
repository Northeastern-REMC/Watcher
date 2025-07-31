from flask import Flask
from watcher import home


def ignite() -> Flask:
    """Driver function to start the Watcher application

    Returns:
        Flask: Flask application with all attached routes and middleware
    """
    app = Flask(__name__)
    
    app.register_blueprint(home.bp)
    
    return app

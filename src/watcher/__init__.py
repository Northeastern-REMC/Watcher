from flask import Flask


def ignite() -> Flask:
    """Driver function to start the Watcher application

    Returns:
        Flask: Flask application with all attached routes and middleware
    """
    app = Flask(__name__)
    
    return app

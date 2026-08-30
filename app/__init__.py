from flask import Flask

from app.routes import api


def create_app() -> Flask:
    application = Flask(__name__)
    application.register_blueprint(api)
    return application


app = create_app()

from flask import Flask, jsonify

from app.routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
    app.register_blueprint(api)

    @app.errorhandler(413)
    def payload_too_large(_error):
        return jsonify(error="Request body is too large (maximum: 64 KiB)."), 413

    return app


app = create_app()

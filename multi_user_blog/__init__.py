import logging

from flask import Flask, redirect, url_for


def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)

    # Register the Auth blueprint
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    # Register the Blog CRUD blueprint.
    from .blog import blog
    app.register_blueprint(blog, url_prefix='/blog')

    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('blog.index'))

    # Add an error handler. This is useful for debugging the live application,
    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return app

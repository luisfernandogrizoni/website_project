import os
from flask import Flask, render_template, flash, url_for, redirect
from root.flask.extensions import database, login_manager, bcrypt, csrf, migrate
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder='../templates',
                static_folder='../static')
    uri = os.environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = uri or f"sqlite:///{os.path.join(app.instance_path, 'banco_associacao.db')}"
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "uma-chave-muito-segura-e-longa")


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-key")

    database.init_app(app)
    migrate.init_app(app, database)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app, database)
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "alert-info"


    from root.flask.blueprints.main_routes import main_bp
    from root.flask.blueprints.social_routes import social_bp
    from root.flask.blueprints.admin_routes import admin_bp
    from root.flask.blueprints.api_routes import api_bp
    from root.flask.blueprints.debug_routes import debug_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(debug_bp)
    register_error_handlers(app)

    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/sistema.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Inicialização do Sistema Casa Acolhida')

    return app

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        database.session.rollback()
        return render_template('500.html', error=e), 500

    @app.errorhandler(403)
    def access_denied(e):
        flash("Acesso negado.", "danger")
        return redirect(url_for('main.inicio'))


from flask import Flask
from flask_cors import CORS
from config import Config

def create_app(config_class=Config):
    """
    Função Application Factory: cria e configura a instância do app Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    
    CORS(app) 

    
    from .api.auth import auth_bp
    from .api.groups import groups_bp
    from .api.projects import projects_bp

    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(groups_bp, url_prefix='/api/groups')
    app.register_blueprint(projects_bp, url_prefix='/api/groups') 

    @app.route('/health')
    def health_check():
        return "Server is healthy!"

    return app
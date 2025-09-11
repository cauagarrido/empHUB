# emphub/__init__.py

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
# Não precisa mais do Supabase aqui, ele pode ser importado nos arquivos de rota se necessário

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    JWTManager(app)

    # --- CORREÇÃO IMPORTANTE AQUI ---
    # Importa os blueprints a partir da nova localização (emphub/api)
    from .api.auth import auth_bp
    from .api.groups import groups_bp
    from .api.projects import projects_bp

    # Registra os blueprints com seus prefixos de URL
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(groups_bp, url_prefix='/api')
    app.register_blueprint(projects_bp, url_prefix='/api')

    # Adiciona uma rota de teste para a página inicial
    @app.route('/')
    def index():
        return "API do empHUB está no ar!"

    return app
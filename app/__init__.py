from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请登录以访问此页面'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    from app.models import User, SiteConfig
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    @app.context_processor
    def inject_globals():
        config = SiteConfig.get_config()
        return dict(
            site_name=config.site_name,
            current_year=datetime.now().year
        )
    
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.forum import forum as forum_blueprint
    app.register_blueprint(forum_blueprint, url_prefix='/forum')
    
    with app.app_context():
        db.create_all()
    
    return app

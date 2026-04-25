from flask import Flask, request, session, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from datetime import datetime
import hashlib

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
            current_year=datetime.now().year,
            max_post_length=config.max_post_length,
            max_comment_length=config.max_comment_length,
            content_preview_length=config.content_preview_length,
            allow_change_username=config.allow_change_username,
            allow_change_password=config.allow_change_password,
            allow_upload_avatar=config.allow_upload_avatar,
            allow_set_title=config.allow_set_title,
            require_access_verify=config.require_access_verify
        )
    
    @app.before_request
    def check_access_verify():
        config = SiteConfig.get_config()
        if config.require_access_verify:
            if request.endpoint and request.endpoint.startswith(('static', 'auth.verify')):
                return None
            token = request.args.get('token') or session.get('access_token')
            if token:
                expected_token = hashlib.sha256(config.access_token.encode()).hexdigest()
                if hashlib.sha256(token.encode()).hexdigest() == expected_token or token == config.access_token:
                    session['access_token'] = config.access_token
                    session.permanent = True
                    return None
            if not session.get('access_token') or session.get('access_token') != config.access_token:
                return render_template('verify.html'), 403
    
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.forum import forum as forum_blueprint
    app.register_blueprint(forum_blueprint, url_prefix='/forum')
    
    with app.app_context():
        db.create_all()
    
    return app

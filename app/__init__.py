from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///self_focus.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(user_id)
    
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.goals import goals_bp
    from app.routes.transactions import transactions_bp
    from app.routes.habits import habits_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(goals_bp, url_prefix='/goals')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(habits_bp, url_prefix='/habits')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

def inject_navigation_helpers():
    def is_nav_active(section, endpoint=None, exclude_endpoints=None):
        """
        Helper function to determine if navigation item should be active
        """
        if endpoint:
            # Check specific endpoint
            return request.endpoint == endpoint
        elif section:
            # Check if current blueprint matches section
            if request.blueprint == section:
                # If exclude_endpoints provided, check if current endpoint should be excluded
                if exclude_endpoints:
                    return request.endpoint not in exclude_endpoints
                return True
        return False
    
    def get_nav_class(section=None, endpoint=None, exclude_endpoints=None):
        """
        Returns 'active' class if navigation should be active
        """
        return 'active' if is_nav_active(section, endpoint, exclude_endpoints) else ''
    
    return dict(is_nav_active=is_nav_active, get_nav_class=get_nav_class)
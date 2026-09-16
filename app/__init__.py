from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import config_by_name
import os

db = SQLAlchemy()
mail = Mail()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    mail.init_app(app)

    from app.models import User, Skill, UserSkill, Match, ExchangeRequest, Session, Review, Notification

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.profile import profile_bp
    from app.routes.skills import skills_bp, seed_skills
    from app.routes.discover import discover_bp
    from app.routes.matches import matches_bp
    from app.routes.exchanges import exchanges_bp
    from app.routes.sessions import sessions_bp
    from app.routes.reviews import reviews_bp
    from app.routes.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(discover_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(exchanges_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(notifications_bp)

    @app.context_processor
    def inject_user():
        from flask import session as flask_session
        from app.models.user import User
        from app.models.notification import Notification
        user_id = flask_session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            unread = Notification.query.filter_by(user_id=user_id, is_read=False).count() if user else 0
            return dict(current_user=user, unread_count=unread)
        return dict(current_user=None, unread_count=0)

    os.makedirs(os.path.join(base_dir, 'static', 'images', 'profiles'), exist_ok=True)

    with app.app_context():
        db.create_all()
        seed_skills()

    return app

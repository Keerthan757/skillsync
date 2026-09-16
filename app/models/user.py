from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='USER')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_email_verified = db.Column(db.Boolean, nullable=False, default=False)

    profile_picture = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    learning_preference = db.Column(db.String(20), nullable=True, default='online')
    availability = db.Column(db.String(50), nullable=True)
    experience_years = db.Column(db.Integer, nullable=True, default=0)

    xp = db.Column(db.Integer, nullable=False, default=0)
    level = db.Column(db.Integer, nullable=False, default=1)
    learning_streak = db.Column(db.Integer, nullable=False, default=0)
    last_active_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    skills_teach = db.relationship('UserSkill', lazy='dynamic',
                                   primaryjoin="and_(User.id==UserSkill.user_id, UserSkill.skill_type=='teach')",
                                   viewonly=True)
    skills_learn = db.relationship('UserSkill', lazy='dynamic',
                                   primaryjoin="and_(User.id==UserSkill.user_id, UserSkill.skill_type=='learn')",
                                   viewonly=True)

    sent_requests = db.relationship('ExchangeRequest', backref='sender', lazy='dynamic',
                                    foreign_keys='ExchangeRequest.sender_id')
    received_requests = db.relationship('ExchangeRequest', backref='receiver', lazy='dynamic',
                                        foreign_keys='ExchangeRequest.receiver_id')

    reviews_given = db.relationship('Review', backref='reviewer', lazy='dynamic',
                                    foreign_keys='Review.reviewer_id')
    reviews_received = db.relationship('Review', backref='reviewed_user', lazy='dynamic',
                                       foreign_keys='Review.reviewed_id')

    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_email_verified': self.is_email_verified,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'location': self.location,
            'learning_preference': self.learning_preference,
            'availability': self.availability,
            'experience_years': self.experience_years,
            'xp': self.xp,
            'level': self.level,
            'learning_streak': self.learning_streak,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.email}>'

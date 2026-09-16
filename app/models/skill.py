from datetime import datetime, timezone
from app import db


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user_skills = db.relationship('UserSkill', backref='skill', lazy='dynamic')

    SKILL_CATEGORIES = [
        'Programming',
        'Web Development',
        'Database',
        'Data Science',
        'Design',
        'Photography',
        'Music',
        'Languages',
        'Business',
        'Marketing',
        'Communication',
        'Other',
    ]

    SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Skill {self.name}>'

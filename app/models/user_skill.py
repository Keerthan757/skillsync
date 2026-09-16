from datetime import datetime, timezone
from app import db


class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False, index=True)
    skill_type = db.Column(db.String(10), nullable=False)
    level = db.Column(db.String(20), nullable=False, default='Beginner')

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'skill_id', 'skill_type', name='uq_user_skill_type'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_id': self.skill_id,
            'skill_type': self.skill_type,
            'level': self.level,
            'skill': self.skill.to_dict() if self.skill else None,
        }

    def __repr__(self):
        return f'<UserSkill {self.user_id}-{self.skill_id} ({self.skill_type})>'

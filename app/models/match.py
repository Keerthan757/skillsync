from datetime import datetime, timezone
from app import db


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    matched_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    match_score = db.Column(db.Float, nullable=False, default=0.0)
    skill_offered_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    skill_wanted_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', foreign_keys=[user_id], backref='matches')
    matched_user = db.relationship('User', foreign_keys=[matched_user_id], backref='matched_by')
    skill_offered = db.relationship('Skill', foreign_keys=[skill_offered_id])
    skill_wanted = db.relationship('Skill', foreign_keys=[skill_wanted_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'matched_user_id': self.matched_user_id,
            'match_score': self.match_score,
            'skill_offered_id': self.skill_offered_id,
            'skill_wanted_id': self.skill_wanted_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Match {self.user_id}-{self.matched_user_id} ({self.match_score}%)>'

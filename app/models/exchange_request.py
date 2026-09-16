from datetime import datetime, timezone
from app import db


class ExchangeRequest(db.Model):
    __tablename__ = 'exchange_requests'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_offered_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    skill_wanted_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    skill_offered = db.relationship('Skill', foreign_keys=[skill_offered_id])
    skill_wanted = db.relationship('Skill', foreign_keys=[skill_wanted_id])

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'skill_offered_id': self.skill_offered_id,
            'skill_wanted_id': self.skill_wanted_id,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sender': self.sender.to_dict() if self.sender else None,
            'receiver': self.receiver.to_dict() if self.receiver else None,
        }

    def __repr__(self):
        return f'<ExchangeRequest {self.sender_id}->{self.receiver_id} ({self.status})>'

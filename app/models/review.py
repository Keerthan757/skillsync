from datetime import datetime, timezone
from app import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    session = db.relationship('Session', backref='reviews')

    __table_args__ = (
        db.UniqueConstraint('session_id', 'reviewer_id', name='uq_session_reviewer'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'reviewer_id': self.reviewer_id,
            'reviewed_id': self.reviewed_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Review {self.reviewer_id}->{self.reviewed_id} ({self.rating}/5)>'

from datetime import datetime, timezone
from app import db


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    exchange_request_id = db.Column(db.Integer, db.ForeignKey('exchange_requests.id'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    learner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)

    session_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    mode = db.Column(db.String(20), nullable=False, default='online')
    meeting_link = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='scheduled')

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    exchange_request = db.relationship('ExchangeRequest', backref='sessions')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='teaching_sessions')
    learner = db.relationship('User', foreign_keys=[learner_id], backref='learning_sessions')
    skill = db.relationship('Skill', backref='sessions')

    def to_dict(self):
        return {
            'id': self.id,
            'exchange_request_id': self.exchange_request_id,
            'teacher_id': self.teacher_id,
            'learner_id': self.learner_id,
            'skill_id': self.skill_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'mode': self.mode,
            'meeting_link': self.meeting_link,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Session {self.id} ({self.status})>'

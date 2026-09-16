from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.exchange_request import ExchangeRequest
from app.models.session import Session
from app.models.skill import Skill
from app.models.notification import Notification
from app.utils.decorators import login_required, get_current_user

sessions_bp = Blueprint('sessions', __name__)


@sessions_bp.route('/sessions')
@login_required
def my_sessions():
    current_user = get_current_user()
    teaching = Session.query.filter_by(teacher_id=current_user.id).order_by(Session.session_date.desc()).all()
    learning = Session.query.filter_by(learner_id=current_user.id).order_by(Session.session_date.desc()).all()
    return render_template('sessions/my_sessions.html', teaching=teaching, learning=learning)


@sessions_bp.route('/sessions/schedule/<int:request_id>', methods=['GET', 'POST'])
@login_required
def schedule_session(request_id):
    current_user = get_current_user()
    er = ExchangeRequest.query.get_or_404(request_id)

    if er.sender_id != current_user.id and er.receiver_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('sessions.my_sessions'))

    if er.status != 'accepted':
        flash('This exchange must be accepted before scheduling.', 'warning')
        return redirect(url_for('exchanges.incoming_requests'))

    if request.method == 'POST':
        session_date = request.form.get('session_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        mode = request.form.get('mode', 'online')
        meeting_link = request.form.get('meeting_link', '').strip()
        location = request.form.get('location', '').strip()

        if not session_date or not start_time or not end_time:
            flash('Please fill in date, start time, and end time.', 'danger')
            return redirect(url_for('sessions.schedule_session', request_id=request_id))

        from datetime import date, time as dt_time
        from werkzeug.datastructures import MultiDict

        try:
            d = list(map(int, session_date.split('-')))
            sd = date(d[0], d[1], d[2])
        except (ValueError, IndexError):
            flash('Invalid date format.', 'danger')
            return redirect(url_for('sessions.schedule_session', request_id=request_id))

        try:
            st_parts = list(map(int, start_time.split(':')))
            st = dt_time(st_parts[0], st_parts[1])
            et_parts = list(map(int, end_time.split(':')))
            et = dt_time(et_parts[0], et_parts[1])
        except (ValueError, IndexError):
            flash('Invalid time format.', 'danger')
            return redirect(url_for('sessions.schedule_session', request_id=request_id))

        skill = er.skill_offered

        teacher_id = current_user.id if current_user.id == er.receiver_id else er.sender_id
        learner_id = er.sender_id if current_user.id == er.receiver_id else er.receiver_id

        session = Session(
            exchange_request_id=er.id,
            teacher_id=teacher_id,
            learner_id=learner_id,
            skill_id=skill.id,
            session_date=sd,
            start_time=st,
            end_time=et,
            mode=mode,
            meeting_link=meeting_link if mode == 'online' else None,
            location=location if mode == 'offline' else None,
            status='scheduled'
        )
        db.session.add(session)

        notif_user = learner_id if current_user.id == teacher_id else teacher_id
        notif = Notification(
            user_id=notif_user,
            title='Session Scheduled',
            message=f'A {skill.name} session has been scheduled for {sd.strftime("%b %d, %Y")}.',
            notification_type='session_scheduled',
            link=url_for('sessions.my_sessions')
        )
        db.session.add(notif)
        db.session.commit()

        flash('Session scheduled successfully!', 'success')
        return redirect(url_for('sessions.my_sessions'))

    from datetime import date as date_type
    today = date_type.today().isoformat()
    return render_template('sessions/schedule.html', exchange_request=er, today=today)


@sessions_bp.route('/sessions/<int:session_id>/cancel', methods=['POST'])
@login_required
def cancel_session(session_id):
    current_user = get_current_user()
    session = Session.query.get_or_404(session_id)

    if session.teacher_id != current_user.id and session.learner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('sessions.my_sessions'))

    if session.status == 'completed':
        flash('Cannot cancel a completed session.', 'warning')
        return redirect(url_for('sessions.my_sessions'))

    session.status = 'cancelled'

    other_id = session.learner_id if current_user.id == session.teacher_id else session.teacher_id
    notif = Notification(
        user_id=other_id,
        title='Session Cancelled',
        message=f'A {session.skill.name} session on {session.session_date.strftime("%b %d, %Y")} has been cancelled.',
        notification_type='session_cancelled',
        link=url_for('sessions.my_sessions')
    )
    db.session.add(notif)
    db.session.commit()

    flash('Session cancelled.', 'info')
    return redirect(url_for('sessions.my_sessions'))


@sessions_bp.route('/sessions/<int:session_id>/complete', methods=['POST'])
@login_required
def complete_session(session_id):
    current_user = get_current_user()
    session = Session.query.get_or_404(session_id)

    if session.teacher_id != current_user.id and session.learner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('sessions.my_sessions'))

    if session.status != 'scheduled':
        flash('This session cannot be marked as complete.', 'warning')
        return redirect(url_for('sessions.my_sessions'))

    session.status = 'completed'

    other_id = session.learner_id if current_user.id == session.teacher_id else session.teacher_id
    notif = Notification(
        user_id=other_id,
        title='Session Completed',
        message=f'Your {session.skill.name} session is complete! Leave a review.',
        notification_type='session_completed',
        link=url_for('reviews.leave_review', session_id=session.id)
    )
    db.session.add(notif)
    db.session.commit()

    flash('Session marked as complete!', 'success')
    return redirect(url_for('reviews.leave_review', session_id=session.id))

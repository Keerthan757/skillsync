from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.exchange_request import ExchangeRequest
from app.models.notification import Notification
from app.utils.decorators import login_required, get_current_user

exchanges_bp = Blueprint('exchanges', __name__)


@exchanges_bp.route('/exchanges')
@login_required
def all_exchanges():
    current_user = get_current_user()
    return redirect(url_for('exchanges.incoming_requests'))


@exchanges_bp.route('/exchanges/incoming')
@login_required
def incoming_requests():
    current_user = get_current_user()
    requests_received = ExchangeRequest.query.filter_by(
        receiver_id=current_user.id
    ).order_by(ExchangeRequest.created_at.desc()).all()
    return render_template('exchanges/incoming.html', requests=requests_received)


@exchanges_bp.route('/exchanges/outgoing')
@login_required
def outgoing_requests():
    current_user = get_current_user()
    requests_sent = ExchangeRequest.query.filter_by(
        sender_id=current_user.id
    ).order_by(ExchangeRequest.created_at.desc()).all()
    return render_template('exchanges/outgoing.html', requests=requests_sent)


@exchanges_bp.route('/exchanges/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    current_user = get_current_user()
    er = ExchangeRequest.query.get_or_404(request_id)

    if er.receiver_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('exchanges.incoming_requests'))

    if er.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('exchanges.incoming_requests'))

    er.status = 'accepted'
    er.updated_at = db.func.now()

    notif = Notification(
        user_id=er.sender_id,
        title='Request Accepted!',
        message=f'{current_user.name} accepted your exchange request.',
        notification_type='exchange_accepted',
        link=url_for('sessions.schedule_session', request_id=er.id)
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Exchange request from {er.sender.name} accepted!', 'success')
    return redirect(url_for('sessions.schedule_session', request_id=er.id))


@exchanges_bp.route('/exchanges/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_request(request_id):
    current_user = get_current_user()
    er = ExchangeRequest.query.get_or_404(request_id)

    if er.receiver_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('exchanges.incoming_requests'))

    if er.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('exchanges.incoming_requests'))

    er.status = 'rejected'
    er.updated_at = db.func.now()

    notif = Notification(
        user_id=er.sender_id,
        title='Request Declined',
        message=f'{current_user.name} declined your exchange request.',
        notification_type='exchange_rejected',
        link=url_for('exchanges.outgoing_requests')
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Exchange request declined.', 'info')
    return redirect(url_for('exchanges.incoming_requests'))


@exchanges_bp.route('/exchanges/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel_request(request_id):
    current_user = get_current_user()
    er = ExchangeRequest.query.get_or_404(request_id)

    if er.sender_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('exchanges.outgoing_requests'))

    if er.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('exchanges.outgoing_requests'))

    er.status = 'cancelled'
    er.updated_at = db.func.now()
    db.session.commit()

    flash('Exchange request cancelled.', 'info')
    return redirect(url_for('exchanges.outgoing_requests'))

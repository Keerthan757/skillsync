from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models.notification import Notification
from app.utils.decorators import login_required, get_current_user

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications')
@login_required
def notifications():
    current_user = get_current_user()
    all_notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template('notifications/notifications.html', notifications=all_notifs, unread_count=unread_count)


@notifications_bp.route('/notifications/mark-read/<int:notif_id>', methods=['POST'])
@login_required
def mark_read(notif_id):
    current_user = get_current_user()
    notif = Notification.query.get_or_404(notif_id)

    if notif.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    notif.is_read = True
    db.session.commit()

    if notif.link:
        return redirect(notif.link)
    return redirect(url_for('notifications.notifications'))


@notifications_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    current_user = get_current_user()
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.notifications'))


@notifications_bp.route('/api/notifications/unread-count')
@login_required
def unread_count():
    current_user = get_current_user()
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

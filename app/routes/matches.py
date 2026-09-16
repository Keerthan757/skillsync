from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models.match import Match
from app.models.exchange_request import ExchangeRequest
from app.models.user import User
from app.models.skill import Skill
from app.models.user_skill import UserSkill
from app.models.notification import Notification
from app.utils.decorators import login_required, get_current_user

matches_bp = Blueprint('matches', __name__)


@matches_bp.route('/matches')
@login_required
def my_matches():
    current_user = get_current_user()

    sent = Match.query.filter_by(user_id=current_user.id).all()
    received = Match.query.filter_by(matched_user_id=current_user.id).all()

    match_ids = set()
    matches = []
    for m in sent:
        if m.id not in match_ids:
            match_ids.add(m.id)
            matches.append({'match': m, 'direction': 'sent', 'other': m.matched_user})
    for m in received:
        if m.id not in match_ids:
            match_ids.add(m.id)
            matches.append({'match': m, 'direction': 'received', 'other': m.user})

    matches.sort(key=lambda x: x['match'].match_score, reverse=True)

    existing_request_ids = set()
    for m in matches:
        other_id = m['other'].id
        er = ExchangeRequest.query.filter(
            db.or_(
                db.and_(ExchangeRequest.sender_id == current_user.id, ExchangeRequest.receiver_id == other_id),
                db.and_(ExchangeRequest.sender_id == other_id, ExchangeRequest.receiver_id == current_user.id),
            )
        ).first()
        if er:
            existing_request_ids.add(other_id)

    return render_template('matches/matches.html', matches=matches, existing_request_ids=existing_request_ids)


@matches_bp.route('/matches/<int:match_id>')
@login_required
def match_detail(match_id):
    current_user = get_current_user()
    match = Match.query.get_or_404(match_id)

    if match.user_id != current_user.id and match.matched_user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('matches.my_matches'))

    other = match.matched_user if match.user_id == current_user.id else match.user

    my_teach = UserSkill.query.filter_by(user_id=current_user.id, skill_type='teach').all()
    my_learn = UserSkill.query.filter_by(user_id=current_user.id, skill_type='learn').all()
    other_teach = UserSkill.query.filter_by(user_id=other.id, skill_type='teach').all()
    other_learn = UserSkill.query.filter_by(user_id=other.id, skill_type='learn').all()

    can_learn_from_them = []
    for ots in other_teach:
        for ml in my_learn:
            if ots.skill_id == ml.skill_id:
                can_learn_from_them.append({'skill': ots.skill, 'their_level': ots.level, 'my_level': ml.level})

    can_teach_them = []
    for ot in other_learn:
        for mt in my_teach:
            if ot.skill_id == mt.skill_id:
                can_teach_them.append({'skill': ot.skill, 'their_level': ot.level, 'my_level': mt.level})

    existing_request = ExchangeRequest.query.filter(
        db.or_(
            db.and_(ExchangeRequest.sender_id == current_user.id, ExchangeRequest.receiver_id == other.id),
            db.and_(ExchangeRequest.sender_id == other.id, ExchangeRequest.receiver_id == current_user.id),
        )
    ).first()

    all_skills = Skill.query.order_by(Skill.name).all()

    return render_template('matches/detail.html',
                         match=match, other=other, can_learn_from_them=can_learn_from_them,
                         can_teach_them=can_teach_them, existing_request=existing_request,
                         all_skills=all_skills)


@matches_bp.route('/matches/<int:match_id>/send-request', methods=['POST'])
@login_required
def send_request(match_id):
    current_user = get_current_user()
    match = Match.query.get_or_404(match_id)

    if match.user_id != current_user.id and match.matched_user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('matches.my_matches'))

    other_id = match.matched_user_id if match.user_id == current_user.id else match.user_id

    existing = ExchangeRequest.query.filter(
        db.or_(
            db.and_(ExchangeRequest.sender_id == current_user.id, ExchangeRequest.receiver_id == other_id),
            db.and_(ExchangeRequest.sender_id == other_id, ExchangeRequest.receiver_id == current_user.id),
        )
    ).first()

    if existing:
        flash('An exchange request already exists with this user.', 'warning')
        return redirect(url_for('matches.match_detail', match_id=match_id))

    skill_offered_id = request.form.get('skill_offered_id', type=int)
    skill_wanted_id = request.form.get('skill_wanted_id', type=int)
    message = request.form.get('message', '').strip()

    if not skill_offered_id or not skill_wanted_id:
        flash('Please select both skills for the exchange.', 'danger')
        return redirect(url_for('matches.match_detail', match_id=match_id))

    er = ExchangeRequest(
        sender_id=current_user.id,
        receiver_id=other_id,
        skill_offered_id=skill_offered_id,
        skill_wanted_id=skill_wanted_id,
        message=message,
        status='pending'
    )
    db.session.add(er)
    db.session.flush()

    notif = Notification(
        user_id=other_id,
        title='New Exchange Request',
        message=f'{current_user.name} wants to exchange skills with you!',
        notification_type='exchange_request',
        link=url_for('exchanges.incoming_requests')
    )
    db.session.add(notif)
    db.session.commit()

    flash('Exchange request sent!', 'success')
    return redirect(url_for('matches.match_detail', match_id=match_id))

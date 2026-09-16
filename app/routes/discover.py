from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import or_, select
from app import db
from app.models.user import User
from app.models.skill import Skill
from app.models.user_skill import UserSkill
from app.utils.decorators import login_required, get_current_user

discover_bp = Blueprint('discover', __name__)


def calculate_match_score(current_user, target_user):
    if not current_user:
        return 0

    score = 0
    max_score = 0

    my_teach = set()
    my_learn = set()
    for us in UserSkill.query.filter_by(user_id=current_user.id, skill_type='teach').all():
        my_teach.add(us.skill_id)
    for us in UserSkill.query.filter_by(user_id=current_user.id, skill_type='learn').all():
        my_learn.add(us.skill_id)

    target_teach = set()
    target_learn = set()
    for us in UserSkill.query.filter_by(user_id=target_user.id, skill_type='teach').all():
        target_teach.add(us.skill_id)
    for us in UserSkill.query.filter_by(user_id=target_user.id, skill_type='learn').all():
        target_learn.add(us.skill_id)

    skill_score = 0
    skill_max = 0

    teach_match = len(my_learn & target_teach)
    learn_match = len(my_teach & target_learn)
    skill_max = max(len(my_learn) + len(my_teach), 1)
    skill_score = min((teach_match + learn_match) / skill_max, 1.0)
    score += skill_score * 50
    max_score += 50

    level_score = 0
    level_count = 0
    for us in UserSkill.query.filter_by(user_id=current_user.id, skill_type='learn').all():
        if us.skill_id in target_teach:
            target_us = UserSkill.query.filter_by(
                user_id=target_user.id, skill_id=us.skill_id, skill_type='teach'
            ).first()
            if target_us:
                levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
                try:
                    diff = abs(levels.index(target_us.level) - levels.index(us.level))
                    level_score += max(0, 1 - diff * 0.25)
                except ValueError:
                    level_score += 0.5
                level_count += 1

    if level_count > 0:
        score += (level_score / level_count) * 20
    max_score += 20

    if current_user.availability and target_user.availability:
        if current_user.availability == target_user.availability:
            score += 15
        elif current_user.availability == 'Flexible' or target_user.availability == 'Flexible':
            score += 10
        else:
            score += 5
    max_score += 15

    if current_user.learning_preference and target_user.learning_preference:
        if current_user.learning_preference == target_user.learning_preference:
            score += 10
        elif current_user.learning_preference == 'both' or target_user.learning_preference == 'both':
            score += 7
    max_score += 10

    reputation_score = 0
    if target_user.xp > 0:
        reputation_score = min(target_user.xp / 100, 1.0)
    score += reputation_score * 5
    max_score += 5

    return round((score / max_score) * 100) if max_score > 0 else 0


@discover_bp.route('/discover')
@login_required
def discover():
    current_user = get_current_user()
    skill_id = request.args.get('skill_id', type=int)
    category = request.args.get('category', '')
    level = request.args.get('level', '')
    availability = request.args.get('availability', '')
    learning_preference = request.args.get('learning_preference', '')
    search = request.args.get('search', '').strip()
    skill_type = request.args.get('skill_type', '')

    query = User.query.filter(User.is_active == True, User.id != current_user.id)

    if skill_id:
        user_ids = select(UserSkill.user_id).where(
            UserSkill.skill_id == skill_id,
            UserSkill.skill_type == skill_type if skill_type else True
        )
        query = query.filter(User.id.in_(user_ids))

    if category:
        skill_ids = select(Skill.id).where(Skill.category == category)
        user_ids = select(UserSkill.user_id).where(
            UserSkill.skill_id.in_(skill_ids)
        )
        query = query.filter(User.id.in_(user_ids))

    if level:
        user_ids = select(UserSkill.user_id).where(
            UserSkill.level == level
        )
        query = query.filter(User.id.in_(user_ids))

    if availability:
        query = query.filter(User.availability == availability)

    if learning_preference:
        query = query.filter(
            or_(User.learning_preference == learning_preference,
                User.learning_preference == 'both')
        )

    if search:
        query = query.filter(
            or_(User.name.ilike(f'%{search}%'), User.location.ilike(f'%{search}%'))
        )

    users = query.all()

    users_with_score = []
    for user in users:
        score = calculate_match_score(current_user, user)
        user_skills_teach = UserSkill.query.filter_by(user_id=user.id, skill_type='teach').all()
        user_skills_learn = UserSkill.query.filter_by(user_id=user.id, skill_type='learn').all()
        users_with_score.append({
            'user': user,
            'match_score': score,
            'skills_teach': user_skills_teach,
            'skills_learn': user_skills_learn,
        })

    users_with_score.sort(key=lambda x: x['match_score'], reverse=True)

    all_skills = Skill.query.order_by(Skill.name).all()
    categories = sorted(Skill.SKILL_CATEGORIES)
    levels = Skill.SKILL_LEVELS

    return render_template('discover/discover.html', users=users_with_score,
                         all_skills=all_skills, categories=categories, levels=levels,
                         selected_skill_id=skill_id, selected_category=category,
                         selected_level=level, selected_availability=availability,
                         selected_preference=learning_preference, search_query=search,
                         selected_skill_type=skill_type)


@discover_bp.route('/api/discover/search')
@login_required
def api_discover_search():
    current_user = get_current_user()
    q = request.args.get('q', '').strip()

    if not q:
        return jsonify([])

    users = User.query.filter(
        User.is_active == True,
        User.id != current_user.id,
        or_(User.name.ilike(f'%{q}%'), User.location.ilike(f'%{q}%'))
    ).limit(10).all()

    results = []
    for user in users:
        score = calculate_match_score(current_user, user)
        results.append({
            'id': user.id,
            'name': user.name,
            'location': user.location,
            'match_score': score,
        })

    return jsonify(results)

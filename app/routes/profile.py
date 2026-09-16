import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User
from app.models.user_skill import UserSkill
from app.utils.decorators import login_required, get_current_user

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_profile_completion(user):
    fields = [
        user.name,
        user.email,
        user.bio,
        user.location,
        user.learning_preference,
        user.availability,
        user.profile_picture,
    ]
    filled = sum(1 for f in fields if f)
    skills = UserSkill.query.filter_by(user_id=user.id).count()
    skill_score = min(skills / 4, 1.0)
    field_score = filled / len(fields)
    return int((field_score * 0.7 + skill_score * 0.3) * 100)


@profile_bp.route('/profile')
@login_required
def view_profile():
    user = get_current_user()
    completion = calculate_profile_completion(user)
    skills_teach = UserSkill.query.filter_by(user_id=user.id, skill_type='teach').all()
    skills_learn = UserSkill.query.filter_by(user_id=user.id, skill_type='learn').all()
    return render_template('user/profile.html', user=user, completion=completion,
                         skills_teach=skills_teach, skills_learn=skills_learn)


@profile_bp.route('/profile/<int:user_id>')
@login_required
def view_public_profile(user_id):
    user = User.query.get_or_404(user_id)
    skills_teach = UserSkill.query.filter_by(user_id=user.id, skill_type='teach').all()
    skills_learn = UserSkill.query.filter_by(user_id=user.id, skill_type='learn').all()
    return render_template('user/public_profile.html', user=user,
                         skills_teach=skills_teach, skills_learn=skills_learn)


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = get_current_user()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        bio = request.form.get('bio', '').strip()
        location = request.form.get('location', '').strip()
        learning_preference = request.form.get('learning_preference', '').strip()
        availability = request.form.get('availability', '').strip()
        experience_years = request.form.get('experience_years', 0)

        errors = []

        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')

        if experience_years and not experience_years.isdigit():
            errors.append('Experience years must be a number.')
        else:
            experience_years = int(experience_years) if experience_years else 0

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('user/edit_profile.html', user=user)

        user.name = name
        user.bio = bio
        user.location = location
        user.learning_preference = learning_preference
        user.availability = availability
        user.experience_years = experience_years

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                upload_dir = os.path.join(current_app.static_folder, 'images', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))

                if user.profile_picture and user.profile_picture != 'default.png':
                    old_path = os.path.join(upload_dir, user.profile_picture)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                user.profile_picture = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))

    return render_template('user/edit_profile.html', user=user)


@profile_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = get_current_user()

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not user.check_password(current_password):
            errors.append('Current password is incorrect.')

        if not new_password or len(new_password) < 6:
            errors.append('New password must be at least 6 characters.')

        if new_password != confirm_password:
            errors.append('New passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('user/change_password.html')

        user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile.view_profile'))

    return render_template('user/change_password.html')

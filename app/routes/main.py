from flask import Blueprint, render_template, session, redirect, url_for
from app.utils.decorators import login_required, get_current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    return render_template('user/dashboard.html', user=user)

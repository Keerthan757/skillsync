import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app import db
from app.models.user import User
from app.models.token import EmailVerificationToken, PasswordResetToken
from app.services.email_service import send_verification_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')

        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Please enter a valid email address.')

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', name=name, email=email)

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = EmailVerificationToken.generate_token(user.id)

        try:
            base_url = request.host_url.rstrip('/')
            send_verification_email(user, token, base_url)
            flash('Account created! Please check your email to verify your account.', 'success')
        except Exception:
            flash('Account created! Email verification is currently unavailable.', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('auth/login.html', email=email)

            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.name

            if remember:
                session.permanent = True

            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('main.dashboard'))

        flash('Invalid email or password.', 'danger')
        return render_template('auth/login.html', email=email)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    verification_token = EmailVerificationToken.query.filter_by(token=token).first()

    if not verification_token:
        return render_template('auth/verify_result.html', success=False,
                             message='Invalid verification link.')

    if not verification_token.is_used and verification_token.is_valid():
        user = User.query.get(verification_token.user_id)
        if user:
            user.is_email_verified = True
            verification_token.use()
            db.session.commit()
            return render_template('auth/verify_result.html', success=True,
                                 message='Email verified successfully!')
        else:
            return render_template('auth/verify_result.html', success=False,
                                 message='User not found.')

    if verification_token.is_used:
        flash('This verification link has already been used.', 'warning')
    else:
        flash('This verification link has expired.', 'warning')

    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and not user.is_email_verified:
            EmailVerificationToken.query.filter_by(user_id=user.id, is_used=False).update({'is_used': True})
            db.session.commit()

            token = EmailVerificationToken.generate_token(user.id)
            try:
                base_url = request.host_url.rstrip('/')
                send_verification_email(user, token, base_url)
            except Exception:
                pass

        flash('If an account exists with this email, a verification link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/resend_verification.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            PasswordResetToken.query.filter_by(user_id=user.id, is_used=False).update({'is_used': True})
            db.session.commit()

            token = PasswordResetToken.generate_token(user.id, expiry_hours=1)
            try:
                base_url = request.host_url.rstrip('/')
                send_password_reset_email(user, token, base_url)
            except Exception:
                pass

        flash('If an account exists with this email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token:
        return render_template('auth/reset_password.html', valid=False,
                             message='Invalid reset link.')

    if not reset_token.is_valid():
        if reset_token.is_used:
            message = 'This reset link has already been used.'
        else:
            message = 'This reset link has expired.'
        return render_template('auth/reset_password.html', valid=False, message=message)

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/reset_password.html', valid=True, token=token)

        user = User.query.get(reset_token.user_id)
        if user:
            user.set_password(password)
            reset_token.use()
            db.session.commit()
            return render_template('auth/reset_password.html', valid=True,
                                 success=True, message='Password reset successfully!')
        else:
            return render_template('auth/reset_password.html', valid=False,
                                 message='User not found.')

    return render_template('auth/reset_password.html', valid=True, token=token)

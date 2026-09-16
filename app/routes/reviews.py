from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.review import Review
from app.models.session import Session
from app.models.user import User
from app.models.notification import Notification
from app.utils.decorators import login_required, get_current_user

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/reviews/<int:user_id>')
def user_reviews(user_id):
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(reviewed_id=user_id).order_by(Review.created_at.desc()).all()

    avg_rating = 0
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    return render_template('reviews/user_reviews.html', user=user, reviews=reviews, avg_rating=avg_rating)


@reviews_bp.route('/reviews/leave/<int:session_id>', methods=['GET', 'POST'])
@login_required
def leave_review(session_id):
    current_user = get_current_user()
    session = Session.query.get_or_404(session_id)

    if session.teacher_id != current_user.id and session.learner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('sessions.my_sessions'))

    if session.status != 'completed':
        flash('You can only review completed sessions.', 'warning')
        return redirect(url_for('sessions.my_sessions'))

    reviewed_id = session.learner_id if current_user.id == session.teacher_id else session.teacher_id

    existing = Review.query.filter_by(session_id=session_id, reviewer_id=current_user.id).first()
    if existing:
        flash('You have already reviewed this session.', 'warning')
        return redirect(url_for('sessions.my_sessions'))

    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()

        if not rating or rating < 1 or rating > 5:
            flash('Please select a rating between 1 and 5.', 'danger')
            return redirect(url_for('reviews.leave_review', session_id=session_id))

        review = Review(
            session_id=session_id,
            reviewer_id=current_user.id,
            reviewed_id=reviewed_id,
            rating=rating,
            comment=comment if comment else None
        )
        db.session.add(review)

        reviewed_user = User.query.get(reviewed_id)
        if reviewed_user:
            all_reviews = Review.query.filter_by(reviewed_id=reviewed_id).all()
            total = sum(r.rating for r in all_reviews) + rating
            count = len(all_reviews) + 1
            reviewed_user.xp = reviewed_user.xp + 10

        notif = Notification(
            user_id=reviewed_id,
            title='New Review',
            message=f'{current_user.name} left you a {rating}-star review!',
            notification_type='review',
            link=url_for('reviews.user_reviews', user_id=reviewed_id)
        )
        db.session.add(notif)
        db.session.commit()

        flash('Review submitted! Thank you for your feedback.', 'success')
        return redirect(url_for('sessions.my_sessions'))

    return render_template('reviews/leave_review.html', session=session, reviewed_id=reviewed_id)

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models.skill import Skill
from app.models.user_skill import UserSkill
from app.models.user import User
from app.utils.decorators import login_required, get_current_user

skills_bp = Blueprint('skills', __name__)


DEFAULT_SKILLS = [
    {'name': 'Python', 'category': 'Programming', 'description': 'General-purpose programming language'},
    {'name': 'JavaScript', 'category': 'Programming', 'description': 'Web programming language'},
    {'name': 'Java', 'category': 'Programming', 'description': 'Object-oriented programming language'},
    {'name': 'C++', 'category': 'Programming', 'description': 'System programming language'},
    {'name': 'Ruby', 'category': 'Programming', 'description': 'Dynamic programming language'},
    {'name': 'Go', 'category': 'Programming', 'description': 'Concurrent programming language'},
    {'name': 'Rust', 'category': 'Programming', 'description': 'Systems programming language'},
    {'name': 'TypeScript', 'category': 'Programming', 'description': 'Typed JavaScript superset'},
    {'name': 'Swift', 'category': 'Programming', 'description': 'Apple development language'},
    {'name': 'Kotlin', 'category': 'Programming', 'description': 'Android development language'},
    {'name': 'HTML', 'category': 'Web Development', 'description': 'Markup language for web pages'},
    {'name': 'CSS', 'category': 'Web Development', 'description': 'Styling language for web pages'},
    {'name': 'React', 'category': 'Web Development', 'description': 'Frontend JavaScript library'},
    {'name': 'Angular', 'category': 'Web Development', 'description': 'Frontend framework'},
    {'name': 'Vue.js', 'category': 'Web Development', 'description': 'Progressive JavaScript framework'},
    {'name': 'Node.js', 'category': 'Web Development', 'description': 'Server-side JavaScript runtime'},
    {'name': 'Django', 'category': 'Web Development', 'description': 'Python web framework'},
    {'name': 'Flask', 'category': 'Web Development', 'description': 'Python micro web framework'},
    {'name': 'REST API', 'category': 'Web Development', 'description': 'RESTful API design'},
    {'name': 'SQL', 'category': 'Database', 'description': 'Structured Query Language'},
    {'name': 'MySQL', 'category': 'Database', 'description': 'Relational database management'},
    {'name': 'PostgreSQL', 'category': 'Database', 'description': 'Advanced relational database'},
    {'name': 'MongoDB', 'category': 'Database', 'description': 'NoSQL document database'},
    {'name': 'Redis', 'category': 'Database', 'description': 'In-memory data store'},
    {'name': 'Excel', 'category': 'Data Science', 'description': 'Spreadsheet and data analysis'},
    {'name': 'Tableau', 'category': 'Data Science', 'description': 'Data visualization tool'},
    {'name': 'Machine Learning', 'category': 'Data Science', 'description': 'AI and ML algorithms'},
    {'name': 'Data Analysis', 'category': 'Data Science', 'description': 'Data analysis techniques'},
    {'name': 'Statistics', 'category': 'Data Science', 'description': 'Statistical analysis'},
    {'name': 'Photoshop', 'category': 'Design', 'description': 'Image editing software'},
    {'name': 'Figma', 'category': 'Design', 'description': 'UI/UX design tool'},
    {'name': 'UI/UX Design', 'category': 'Design', 'description': 'User interface and experience design'},
    {'name': 'Adobe Illustrator', 'category': 'Design', 'description': 'Vector graphics editor'},
    {'name': 'Blender', 'category': 'Design', 'description': '3D modeling and animation'},
    {'name': 'Photography', 'category': 'Photography', 'description': 'Digital photography skills'},
    {'name': 'Lightroom', 'category': 'Photography', 'description': 'Photo editing and management'},
    {'name': 'Guitar', 'category': 'Music', 'description': 'Guitar playing'},
    {'name': 'Piano', 'category': 'Music', 'description': 'Piano playing'},
    {'name': 'Music Production', 'category': 'Music', 'description': 'Digital music creation'},
    {'name': 'English', 'category': 'Languages', 'description': 'English language'},
    {'name': 'Spanish', 'category': 'Languages', 'description': 'Spanish language'},
    {'name': 'French', 'category': 'Languages', 'description': 'French language'},
    {'name': 'German', 'category': 'Languages', 'description': 'German language'},
    {'name': 'Japanese', 'category': 'Languages', 'description': 'Japanese language'},
    {'name': 'Mandarin', 'category': 'Languages', 'description': 'Mandarin Chinese language'},
    {'name': 'Business Strategy', 'category': 'Business', 'description': 'Business planning and strategy'},
    {'name': 'Project Management', 'category': 'Business', 'description': 'Project planning and execution'},
    {'name': 'Public Speaking', 'category': 'Communication', 'description': 'Presentation and speaking skills'},
    {'name': 'Writing', 'category': 'Communication', 'description': 'Written communication skills'},
    {'name': 'Digital Marketing', 'category': 'Marketing', 'description': 'Online marketing strategies'},
    {'name': 'SEO', 'category': 'Marketing', 'description': 'Search engine optimization'},
    {'name': 'Social Media Marketing', 'category': 'Marketing', 'description': 'Social media strategies'},
    {'name': 'Git', 'category': 'Programming', 'description': 'Version control system'},
    {'name': 'Docker', 'category': 'Web Development', 'description': 'Containerization platform'},
    {'name': 'AWS', 'category': 'Web Development', 'description': 'Amazon Web Services cloud'},
    {'name': 'Linux', 'category': 'Programming', 'description': 'Linux operating system'},
]


def seed_skills():
    for skill_data in DEFAULT_SKILLS:
        existing = Skill.query.filter_by(name=skill_data['name']).first()
        if not existing:
            skill = Skill(
                name=skill_data['name'],
                category=skill_data['category'],
                description=skill_data['description']
            )
            db.session.add(skill)
    db.session.commit()

    seed_demo_users()


def seed_demo_users():
    if User.query.filter_by(is_email_verified=True).count() > 1:
        return

    demo_users = [
        {
            'name': 'Priya Sharma',
            'email': 'priya@example.com',
            'bio': 'Full-stack developer passionate about teaching Python and learning new frameworks.',
            'location': 'Bangalore, India',
            'availability': 'Weekends',
            'learning_preference': 'online',
            'experience_years': 5,
            'xp': 85,
            'level': 4,
            'teach': [('Python', 'Expert'), ('JavaScript', 'Advanced'), ('React', 'Intermediate')],
            'learn': [('Go', 'Beginner'), ('Machine Learning', 'Intermediate')],
        },
        {
            'name': 'Marcus Chen',
            'email': 'marcus@example.com',
            'bio': 'UX designer by day, musician by night. Love collaborating on creative projects.',
            'location': 'San Francisco, USA',
            'availability': 'Evenings',
            'learning_preference': 'online',
            'experience_years': 4,
            'xp': 62,
            'level': 3,
            'teach': [('UI/UX Design', 'Expert'), ('Figma', 'Advanced'), ('Photoshop', 'Intermediate')],
            'learn': [('Python', 'Beginner'), ('Guitar', 'Intermediate')],
        },
        {
            'name': 'Aisha Okafor',
            'email': 'aisha@example.com',
            'bio': 'Data scientist with a love for languages. Always looking to exchange skills!',
            'location': 'Lagos, Nigeria',
            'availability': 'Flexible',
            'learning_preference': 'both',
            'experience_years': 3,
            'xp': 74,
            'level': 4,
            'teach': [('Machine Learning', 'Advanced'), ('Data Analysis', 'Expert'), ('Python', 'Advanced')],
            'learn': [('Japanese', 'Beginner'), ('Public Speaking', 'Intermediate')],
        },
        {
            'name': 'Tom Eriksson',
            'email': 'tom@example.com',
            'bio': 'Backend engineer specializing in cloud infrastructure. Teaching Docker & AWS.',
            'location': 'Stockholm, Sweden',
            'availability': 'Weekdays',
            'learning_preference': 'online',
            'experience_years': 6,
            'xp': 91,
            'level': 5,
            'teach': [('Docker', 'Expert'), ('AWS', 'Expert'), ('Linux', 'Advanced')],
            'learn': [('React', 'Intermediate'), ('Spanish', 'Beginner')],
        },
        {
            'name': 'Sofia Rodriguez',
            'email': 'sofia@example.com',
            'bio': 'Digital marketer and SEO specialist. Fluent in 3 languages.',
            'location': 'Barcelona, Spain',
            'availability': 'Weekends',
            'learning_preference': 'both',
            'experience_years': 4,
            'xp': 55,
            'level': 3,
            'teach': [('Digital Marketing', 'Expert'), ('SEO', 'Advanced'), ('Spanish', 'Expert')],
            'learn': [('Python', 'Beginner'), ('Photography', 'Intermediate')],
        },
        {
            'name': 'Kenji Tanaka',
            'email': 'kenji@example.com',
            'bio': 'Mobile developer from Tokyo. Expert in Swift and Kotlin, learning web dev.',
            'location': 'Tokyo, Japan',
            'availability': 'Evenings',
            'learning_preference': 'online',
            'experience_years': 5,
            'xp': 78,
            'level': 4,
            'teach': [('Swift', 'Expert'), ('Kotlin', 'Advanced'), ('Japanese', 'Expert')],
            'learn': [('Vue.js', 'Beginner'), ('CSS', 'Intermediate')],
        },
        {
            'name': 'Emma Wilson',
            'email': 'emma@example.com',
            'bio': 'Project manager and business strategist. Love helping others organize their work.',
            'location': 'London, UK',
            'availability': 'Weekdays',
            'learning_preference': 'online',
            'experience_years': 7,
            'xp': 95,
            'level': 5,
            'teach': [('Project Management', 'Expert'), ('Business Strategy', 'Expert'), ('Public Speaking', 'Advanced')],
            'learn': [('JavaScript', 'Beginner'), ('Data Analysis', 'Intermediate')],
        },
        {
            'name': 'Raj Patel',
            'email': 'raj@example.com',
            'bio': 'Music producer and audio engineer. Teach music production, learn to code.',
            'location': 'Mumbai, India',
            'availability': 'Flexible',
            'learning_preference': 'both',
            'experience_years': 3,
            'xp': 45,
            'level': 3,
            'teach': [('Music Production', 'Expert'), ('Guitar', 'Advanced'), ('Piano', 'Intermediate')],
            'learn': [('Python', 'Beginner'), ('JavaScript', 'Beginner')],
        },
        {
            'name': 'Lena Mueller',
            'email': 'lena@example.com',
            'bio': 'Frontend developer and design enthusiast. Passionate about accessible UIs.',
            'location': 'Berlin, Germany',
            'availability': 'Weekends',
            'learning_preference': 'online',
            'experience_years': 3,
            'xp': 58,
            'level': 3,
            'teach': [('HTML', 'Expert'), ('CSS', 'Expert'), ('React', 'Advanced'), ('Figma', 'Intermediate')],
            'learn': [('Machine Learning', 'Beginner'), ('German', 'Expert')],
        },
        {
            'name': 'David Kim',
            'email': 'david@example.com',
            'bio': 'Database administrator and SQL expert. Also into photography.',
            'location': 'Seoul, South Korea',
            'availability': 'Evenings',
            'learning_preference': 'online',
            'experience_years': 5,
            'xp': 70,
            'level': 4,
            'teach': [('SQL', 'Expert'), ('PostgreSQL', 'Expert'), ('MongoDB', 'Advanced'), ('Photography', 'Advanced')],
            'learn': [('React', 'Intermediate'), ('Writing', 'Beginner')],
        },
    ]

    for data in demo_users:
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            continue

        user = User(
            name=data['name'],
            email=data['email'],
            is_active=True,
            is_email_verified=True,
            bio=data['bio'],
            location=data['location'],
            availability=data['availability'],
            learning_preference=data['learning_preference'],
            experience_years=data['experience_years'],
            xp=data['xp'],
            level=data['level'],
        )
        user.set_password('demo1234')
        db.session.add(user)
        db.session.flush()

        for skill_name, level in data['teach']:
            skill = Skill.query.filter_by(name=skill_name).first()
            if skill:
                us = UserSkill(user_id=user.id, skill_id=skill.id, skill_type='teach', level=level)
                db.session.add(us)

        for skill_name, level in data['learn']:
            skill = Skill.query.filter_by(name=skill_name).first()
            if skill:
                us = UserSkill(user_id=user.id, skill_id=skill.id, skill_type='learn', level=level)
                db.session.add(us)

    db.session.commit()


@skills_bp.route('/skills')
def browse_skills():
    category = request.args.get('category', '')
    search = request.args.get('search', '').strip()

    query = Skill.query

    if category:
        query = query.filter_by(category=category)

    if search:
        query = query.filter(Skill.name.ilike(f'%{search}%'))

    skills = query.order_by(Skill.name).all()
    categories = sorted(Skill.SKILL_CATEGORIES)

    return render_template('skills/browse.html', skills=skills, categories=categories,
                         selected_category=category, search_query=search)


@skills_bp.route('/skills/<int:skill_id>')
def skill_detail(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    teachers = UserSkill.query.filter_by(skill_id=skill.id, skill_type='teach').all()
    learners = UserSkill.query.filter_by(skill_id=skill.id, skill_type='learn').all()
    return render_template('skills/detail.html', skill=skill, teachers=teachers, learners=learners)


@skills_bp.route('/my-skills')
@login_required
def my_skills():
    user = get_current_user()
    skills_teach = UserSkill.query.filter_by(user_id=user.id, skill_type='teach').all()
    skills_learn = UserSkill.query.filter_by(user_id=user.id, skill_type='learn').all()
    all_skills = Skill.query.order_by(Skill.name).all()
    categories = sorted(Skill.SKILL_CATEGORIES)
    return render_template('skills/my_skills.html', skills_teach=skills_teach,
                         skills_learn=skills_learn, all_skills=all_skills, categories=categories)


@skills_bp.route('/my-skills/add', methods=['POST'])
@login_required
def add_skill():
    user = get_current_user()
    skill_id = request.form.get('skill_id', type=int)
    skill_type = request.form.get('skill_type', '').strip()
    level = request.form.get('level', 'Beginner').strip()

    if not skill_id or skill_type not in ('teach', 'learn'):
        flash('Invalid skill data.', 'danger')
        return redirect(url_for('skills.my_skills'))

    if level not in Skill.SKILL_LEVELS:
        level = 'Beginner'

    existing = UserSkill.query.filter_by(
        user_id=user.id, skill_id=skill_id, skill_type=skill_type
    ).first()

    if existing:
        flash('You already have this skill.', 'warning')
        return redirect(url_for('skills.my_skills'))

    user_skill = UserSkill(user_id=user.id, skill_id=skill_id, skill_type=skill_type, level=level)
    db.session.add(user_skill)
    db.session.commit()
    flash('Skill added successfully!', 'success')
    return redirect(url_for('skills.my_skills'))


@skills_bp.route('/my-skills/add-custom', methods=['POST'])
@login_required
def add_custom_skill():
    user = get_current_user()
    skill_name = request.form.get('skill_name', '').strip()
    skill_type = request.form.get('skill_type', '').strip()
    level = request.form.get('level', 'Beginner').strip()
    category = request.form.get('category', 'Other').strip()

    errors = []

    if not skill_name or len(skill_name) < 2:
        errors.append('Skill name must be at least 2 characters.')

    if skill_type not in ('teach', 'learn'):
        errors.append('Invalid skill type.')

    if level not in Skill.SKILL_LEVELS:
        level = 'Beginner'

    if category not in Skill.SKILL_CATEGORIES:
        category = 'Other'

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('skills.my_skills'))

    skill = Skill.query.filter_by(name=skill_name).first()
    if not skill:
        skill = Skill(name=skill_name, category=category, description=f'{skill_name} skill')
        db.session.add(skill)
        db.session.flush()

    existing = UserSkill.query.filter_by(
        user_id=user.id, skill_id=skill.id, skill_type=skill_type
    ).first()

    if existing:
        flash('You already have this skill.', 'warning')
        return redirect(url_for('skills.my_skills'))

    user_skill = UserSkill(user_id=user.id, skill_id=skill.id, skill_type=skill_type, level=level)
    db.session.add(user_skill)
    db.session.commit()
    flash(f'Custom skill "{skill_name}" added!', 'success')
    return redirect(url_for('skills.my_skills'))


@skills_bp.route('/my-skills/<int:user_skill_id>/update', methods=['POST'])
@login_required
def update_skill(user_skill_id):
    user = get_current_user()
    user_skill = UserSkill.query.get_or_404(user_skill_id)

    if user_skill.user_id != user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('skills.my_skills'))

    level = request.form.get('level', 'Beginner').strip()
    if level in Skill.SKILL_LEVELS:
        user_skill.level = level
        db.session.commit()
        flash('Skill level updated!', 'success')

    return redirect(url_for('skills.my_skills'))


@skills_bp.route('/my-skills/<int:user_skill_id>/remove', methods=['POST'])
@login_required
def remove_skill(user_skill_id):
    user = get_current_user()
    user_skill = UserSkill.query.get_or_404(user_skill_id)

    if user_skill.user_id != user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('skills.my_skills'))

    db.session.delete(user_skill)
    db.session.commit()
    flash('Skill removed.', 'info')
    return redirect(url_for('skills.my_skills'))


@skills_bp.route('/api/skills/search')
def api_search_skills():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    skills = Skill.query.filter(Skill.name.ilike(f'%{q}%')).limit(20).all()
    return jsonify([s.to_dict() for s in skills])

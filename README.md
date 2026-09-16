# SkillSync – Smart Peer-to-Peer Skill Exchange Platform

A full-stack web application that connects people who want to learn skills with people who can teach them.

## Features

- User registration and authentication
- Email verification
- Password reset
- Skill management
- Smart matching algorithm
- Skill exchange requests
- Session scheduling
- Reviews and ratings
- Notifications
- Gamification (XP, badges, levels)
- Admin dashboard
- REST API

## Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend:** Python, Flask
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** Session-based with secure password hashing
- **Email:** Gmail SMTP

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/skillsync.git
cd skillsync
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
copy .env.example .env
# Edit .env with your settings
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and visit:
```
http://127.0.0.1:5000
```

## Project Structure

```
SkillSync/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── matching/
├── templates/
│   ├── auth/
│   ├── user/
│   └── admin/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── instance/
    └── skillsync.db
```

## License

MIT License

from flask import render_template_string
from flask_mail import Message
from app import mail


VERIFICATION_EMAIL_SUBJECT = 'SkillSync - Verify Your Email'

VERIFICATION_EMAIL_BODY = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #0d6efd; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; text-align: center; }
        .btn { display: inline-block; padding: 12px 30px; background: #0d6efd; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
        .footer { padding: 15px; text-align: center; font-size: 12px; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SkillSync</h1>
        </div>
        <div class="content">
            <h2>Verify Your Email Address</h2>
            <p>Thank you for registering with SkillSync! Please click the button below to verify your email address.</p>
            <a href="{{ verification_url }}" class="btn">Verify Email</a>
            <p style="font-size: 14px; color: #666;">This link will expire in 24 hours.</p>
            <p style="font-size: 14px; color: #666;">If you did not create an account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 SkillSync. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
'''


def send_verification_email(user, token, base_url='http://127.0.0.1:5000'):
    verification_url = f'{base_url}/verify-email/{token.token}'
    html_body = render_template_string(VERIFICATION_EMAIL_BODY, verification_url=verification_url)
    msg = Message(
        subject=VERIFICATION_EMAIL_SUBJECT,
        recipients=[user.email],
        html=html_body
    )
    mail.send(msg)


def send_password_reset_email(user, token, base_url='http://127.0.0.1:5000'):
    reset_url = f'{base_url}/reset-password/{token.token}'
    html_body = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
            .container {{ max-width: 500px; margin: auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: #0d6efd; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; text-align: center; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
            .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SkillSync</h1>
            </div>
            <div class="content">
                <h2>Reset Your Password</h2>
                <p>You requested a password reset. Click the button below to create a new password.</p>
                <a href="{reset_url}" class="btn">Reset Password</a>
                <p style="font-size: 14px; color: #666;">This link will expire in 1 hour.</p>
                <p style="font-size: 14px; color: #666;">If you did not request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2026 SkillSync. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    msg = Message(
        subject='SkillSync - Reset Your Password',
        recipients=[user.email],
        html=html_body
    )
    mail.send(msg)

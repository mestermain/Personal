import os
import re
import smtplib
from email.mime.text import MIMEText
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from models import db, SiteProfile, Skill, Project, Research, Experience, Message

main_bp = Blueprint('main', __name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def send_notification_email(sender_name, sender_email, subject, message_body):
    """Optional SMTP email notification to admin if MAIL_SERVER is configured."""
    mail_server = os.environ.get('MAIL_SERVER')
    mail_port = int(os.environ.get('MAIL_PORT', 587))
    mail_user = os.environ.get('MAIL_USERNAME')
    mail_password = os.environ.get('MAIL_PASSWORD')
    admin_email = os.environ.get('ADMIN_EMAIL') or mail_user

    if mail_server and mail_user and mail_password and admin_email:
        try:
            msg_content = f"New Portfolio Inquiry\n\nFrom: {sender_name} ({sender_email})\nSubject: {subject}\n\nMessage:\n{message_body}"
            mime_msg = MIMEText(msg_content)
            mime_msg['Subject'] = f"[Portfolio Contact] {subject}"
            mime_msg['From'] = mail_user
            mime_msg['To'] = admin_email

            with smtplib.SMTP(mail_server, mail_port) as server:
                server.starttls()
                server.login(mail_user, mail_password)
                server.sendmail(mail_user, [admin_email], mime_msg.as_string())
        except Exception as e:
            current_app.logger.warning(f"Failed to send email notification: {e}")

@main_bp.route('/')
def index():
    profile = SiteProfile.query.first()
    if not profile:
        profile = SiteProfile()

    # Dynamic Skills & Categories
    skills = Skill.query.order_by(Skill.order_index).all()
    skills_by_category = {}
    for skill in skills:
        cat = skill.category.strip() if skill.category else "General"
        if cat not in skills_by_category:
            skills_by_category[cat] = []
        skills_by_category[cat].append(skill)

    # Real counts
    projects = Project.query.order_by(Project.order_index, Project.created_at.desc()).all()
    featured_projects = [p for p in projects if p.is_featured]
    projects_count = len(projects)

    research_papers = Research.query.order_by(Research.order_index, Research.created_at.desc()).all()
    research_count = len(research_papers)

    project_categories = list(set(p.category for p in projects if p.category))

    work_experience = Experience.query.filter_by(type='work').order_by(Experience.order_index, Experience.id.desc()).all()
    education_experience = Experience.query.filter_by(type='education').order_by(Experience.order_index, Experience.id.desc()).all()

    return render_template('index.html',
                           profile=profile,
                           skills_by_category=skills_by_category,
                           projects=projects,
                           featured_projects=featured_projects,
                           projects_count=projects_count,
                           research_papers=research_papers,
                           research_count=research_count,
                           project_categories=project_categories,
                           work_experience=work_experience,
                           education_experience=education_experience)

@main_bp.route('/project/<slug>')
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    profile = SiteProfile.query.first()
    related_projects = Project.query.filter(Project.id != project.id, Project.category == project.category).limit(3).all()
    
    return render_template('project_detail.html', 
                           project=project, 
                           profile=profile, 
                           related_projects=related_projects)

@main_bp.route('/research/<int:research_id>')
def research_detail(research_id):
    paper = Research.query.get_or_404(research_id)
    profile = SiteProfile.query.first()
    related_papers = Research.query.filter(Research.id != paper.id).order_by(Research.id.desc()).limit(3).all()
    
    return render_template('research_detail.html',
                           paper=paper,
                           profile=profile,
                           related_papers=related_papers)

@main_bp.route('/contact', methods=['POST'])
def contact():
    # Anti-Spam Honeypot Check
    honeypot = request.form.get('website_hp', '').strip()
    if honeypot:
        # Bot filled in hidden honeypot field, silently return fake success
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'message': 'Thank you! Your message has been sent successfully.'})
        return redirect(url_for('main.index') + '#contact')

    sender_name = request.form.get('name', '').strip()[:100]
    sender_email = request.form.get('email', '').strip()[:120]
    subject = request.form.get('subject', 'Portfolio Contact Inquiry').strip()[:200]
    message_body = request.form.get('message', '').strip()[:5000]

    # Required fields check
    if not sender_name or not sender_email or not message_body:
        msg = 'Please fill in all required fields (Name, Email, and Message).'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': msg}), 400
        flash(msg, 'danger')
        return redirect(url_for('main.index') + '#contact')

    # Email format validation
    if not EMAIL_REGEX.match(sender_email):
        msg = 'Please enter a valid email address.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': msg}), 422
        flash(msg, 'danger')
        return redirect(url_for('main.index') + '#contact')

    new_msg = Message(
        sender_name=sender_name,
        sender_email=sender_email,
        subject=subject or 'Portfolio Contact Inquiry',
        message_body=message_body
    )
    db.session.add(new_msg)
    db.session.commit()

    # Optional email notification
    send_notification_email(sender_name, sender_email, subject, message_body)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Thank you! Your message has been sent successfully.'})

    flash('Thank you! Your message has been sent successfully.', 'success')
    return redirect(url_for('main.index') + '#contact')

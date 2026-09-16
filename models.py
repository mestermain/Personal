from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SiteProfile(db.Model):
    __tablename__ = 'site_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False, default="Talha Sadeeq")
    job_title = db.Column(db.String(150), nullable=False, default="Full Stack Developer & AI Engineer")
    hero_headline = db.Column(db.String(200), nullable=False, default="Crafting Modern Web Experiences & Intelligent Systems")
    hero_subheadline = db.Column(db.Text, nullable=True, default="Passionate software engineer specializing in Python, Flask, Machine Learning, and building scalable full-stack applications with elegant UI/UX design.")
    about_summary = db.Column(db.Text, nullable=True, default="I build robust, high-performance web applications, ML models, and backend systems.")
    about_detailed = db.Column(db.Text, nullable=True, default="With years of software development experience, I bring ideas to life using cutting-edge web technologies, artificial intelligence, clean architecture, and intuitive user interfaces.")
    location = db.Column(db.String(100), default="San Francisco, CA")
    email = db.Column(db.String(120), default="contact@example.com")
    phone = db.Column(db.String(30), default="+1 (555) 019-2834")
    avatar_url = db.Column(db.String(500), default="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80")
    resume_url = db.Column(db.String(500), default="#")
    github_url = db.Column(db.String(300), default="https://github.com")
    linkedin_url = db.Column(db.String(300), default="https://linkedin.com")
    leetcode_url = db.Column(db.String(300), default="https://leetcode.com")
    years_experience = db.Column(db.Integer, default=5)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=False, default="Frontend", index=True)
    proficiency = db.Column(db.Integer, default=90)
    icon_class = db.Column(db.String(100), default="fas fa-code")
    order_index = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default="Web Application", index=True)
    short_description = db.Column(db.Text, nullable=False)
    detailed_description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    github_url = db.Column(db.String(300), default="#")
    demo_url = db.Column(db.String(300), default="#")
    tags = db.Column(db.String(250), default="Python, Flask, Tailwind CSS")
    is_featured = db.Column(db.Boolean, default=True, index=True)
    order_index = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Research(db.Model):
    __tablename__ = 'research_papers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    conference_or_journal = db.Column(db.String(150), nullable=False)
    publication_year = db.Column(db.String(20), nullable=False, default="2026")
    abstract = db.Column(db.Text, nullable=False)
    paper_url = db.Column(db.String(500), default="#")
    pdf_url = db.Column(db.String(500), default="#")
    tags = db.Column(db.String(250), default="Deep Learning, Computer Vision, AI")
    is_featured = db.Column(db.Boolean, default=True, index=True)
    order_index = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Experience(db.Model):
    __tablename__ = 'experiences'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False, default="work", index=True)
    title_or_degree = db.Column(db.String(150), nullable=False)
    organization = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), default="Remote")
    period = db.Column(db.String(80), nullable=False, default="2022 - Present")
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)


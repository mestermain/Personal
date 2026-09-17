import os
import re
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, AdminUser, SiteProfile, Skill, Project, Research, Experience, Message, SiteSetting
from utils import convert_gdrive_url

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage):
    if not file_storage or file_storage.filename == '':
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Invalid file format. Only PNG, JPG, JPEG, GIF, WEBP, SVG, and PDF files are allowed.")
    
    unique_name = f"{uuid.uuid4().hex[:12]}_{secure_filename(file_storage.filename)}"
    upload_dir = os.path.join(current_app.static_folder, 'uploads')
    try:
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_name)
        file_storage.save(file_path)
        return url_for('static', filename=f'uploads/{unique_name}')
    except Exception as e:
        current_app.logger.error(f"Failed to save upload locally: {e}")
        raise ValueError("File upload failed: Serverless platforms (like Vercel) have read-only storage. Please paste an Image URL instead.")

def delete_uploaded_file(file_url):
    if not file_url or not file_url.startswith('/static/uploads/'):
        return
    filename = os.path.basename(file_url)
    file_path = os.path.join(current_app.static_folder, 'uploads', filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            current_app.logger.warning(f"Could not remove old upload file: {e}")

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    profile = SiteProfile.query.first()
    unread_messages_count = Message.query.filter_by(is_read=False).count()
    total_projects = Project.query.count()
    total_skills = Skill.query.count()
    total_research = Research.query.count()
    total_experience = Experience.query.count()
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           profile=profile,
                           unread_messages_count=unread_messages_count,
                           total_projects=total_projects,
                           total_skills=total_skills,
                           total_research=total_research,
                           total_experience=total_experience,
                           recent_messages=recent_messages)

# --- PROFILE & BIO MANAGEMENT ---
@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = SiteProfile.query.first()
    if not profile:
        profile = SiteProfile()
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        job_title = request.form.get('job_title', '').strip()

        if not full_name or not job_title:
            flash('Full Name and Job Title are required.', 'danger')
            return redirect(url_for('admin.profile'))

        old_avatar_url = profile.avatar_url
        profile.full_name = full_name
        profile.job_title = job_title
        profile.hero_headline = request.form.get('hero_headline', '').strip()
        profile.hero_subheadline = request.form.get('hero_subheadline', '').strip()
        profile.about_summary = request.form.get('about_summary', '').strip()
        profile.about_detailed = request.form.get('about_detailed', '').strip()
        profile.location = request.form.get('location', '').strip()
        profile.email = request.form.get('email', '').strip()
        profile.phone = request.form.get('phone', '').strip()

        avatar_input = request.form.get('avatar_url', '').strip()
        if avatar_input:
            profile.avatar_url = convert_gdrive_url(avatar_input)

        profile.resume_url = request.form.get('resume_url', '').strip()
        profile.github_url = request.form.get('github_url', '').strip()
        profile.linkedin_url = request.form.get('linkedin_url', '').strip()
        profile.leetcode_url = request.form.get('leetcode_url', '').strip()
        
        try:
            profile.years_experience = int(request.form.get('years_experience', 5))
        except (ValueError, TypeError):
            profile.years_experience = 5

        # Handle avatar image file upload if provided
        avatar_file = request.files.get('avatar_file')
        if avatar_file and avatar_file.filename != '':
            try:
                new_avatar_url = save_uploaded_file(avatar_file)
                if new_avatar_url:
                    if old_avatar_url and old_avatar_url != new_avatar_url:
                        delete_uploaded_file(old_avatar_url)
                    profile.avatar_url = new_avatar_url
            except Exception as ve:
                flash(str(ve), 'danger')
                return redirect(url_for('admin.profile'))

        try:
            db.session.commit()
            flash('Profile and Bio details updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving profile: {e}")
            flash(f'Database update error: {str(e)}', 'danger')
            
        return redirect(url_for('admin.profile'))

    return render_template('admin/profile.html', profile=profile)

# --- DYNAMIC SKILLS MANAGEMENT ---
@admin_bp.route('/skills')
@login_required
def skills():
    all_skills = Skill.query.order_by(Skill.category, Skill.order_index).all()
    # Unique existing skill categories for datalist auto-complete
    existing_categories = sorted(list(set(s.category.strip() for s in all_skills if s.category)))
    return render_template('admin/skills.html', skills=all_skills, existing_categories=existing_categories)

@admin_bp.route('/skills/add', methods=['POST'])
@login_required
def add_skill():
    name = request.form.get('name', '').strip()
    category = request.form.get('category', 'General').strip()
    proficiency = int(request.form.get('proficiency', 85))
    icon_class = request.form.get('icon_class', 'fas fa-code').strip()
    order_index = int(request.form.get('order_index', 0))

    if name:
        new_skill = Skill(name=name, category=category, proficiency=proficiency, 
                          icon_class=icon_class, order_index=order_index)
        db.session.add(new_skill)
        db.session.commit()
        flash(f'Skill "{name}" added under category "{category}"!', 'success')
    else:
        flash('Skill name cannot be empty.', 'danger')
        
    return redirect(url_for('admin.skills'))

@admin_bp.route('/skills/edit/<int:id>', methods=['POST'])
@login_required
def edit_skill(id):
    skill = Skill.query.get_or_404(id)
    skill.name = request.form.get('name', '').strip()
    skill.category = request.form.get('category', skill.category).strip()
    skill.proficiency = int(request.form.get('proficiency', skill.proficiency))
    skill.icon_class = request.form.get('icon_class', skill.icon_class).strip()
    skill.order_index = int(request.form.get('order_index', skill.order_index))
    
    db.session.commit()
    flash(f'Skill "{skill.name}" updated successfully!', 'success')
    return redirect(url_for('admin.skills'))

@admin_bp.route('/skills/delete/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    name = skill.name
    db.session.delete(skill)
    db.session.commit()
    flash(f'Skill "{name}" deleted successfully.', 'info')
    return redirect(url_for('admin.skills'))

# --- PROJECTS MANAGEMENT ---
@admin_bp.route('/projects')
@login_required
def projects():
    all_projects = Project.query.order_by(Project.order_index, Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=all_projects)

@admin_bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Web Application').strip()
        short_description = request.form.get('short_description', '').strip()
        detailed_description = request.form.get('detailed_description', '').strip()
        image_url = convert_gdrive_url(request.form.get('image_url', '').strip())
        github_url = request.form.get('github_url', '').strip()
        demo_url = request.form.get('demo_url', '').strip()
        tags = request.form.get('tags', '').strip()
        is_featured = True if request.form.get('is_featured') else False
        order_index = int(request.form.get('order_index', 0))

        if not title or not short_description:
            flash('Project Title and Short Description are required.', 'danger')
            return redirect(url_for('admin.add_project'))

        image_file = request.files.get('image_file')
        if image_file and image_file.filename != '':
            try:
                uploaded_url = save_uploaded_file(image_file)
                if uploaded_url:
                    image_url = uploaded_url
            except Exception as ve:
                flash(str(ve), 'danger')
                return redirect(url_for('admin.add_project'))

        if not image_url:
            image_url = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80'

        slug = slugify(title)
        existing = Project.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{int(db.session.query(db.func.max(Project.id)).scalar() or 0) + 1}"

        new_project = Project(
            title=title,
            slug=slug,
            category=category,
            short_description=short_description,
            detailed_description=detailed_description,
            image_url=image_url,
            github_url=github_url,
            demo_url=demo_url,
            tags=tags,
            is_featured=is_featured,
            order_index=order_index
        )
        db.session.add(new_project)
        db.session.commit()
        flash(f'Project "{title}" created successfully!', 'success')
        return redirect(url_for('admin.projects'))

    return render_template('admin/project_form.html', project=None)

@admin_bp.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Project Title cannot be empty.', 'danger')
            return redirect(url_for('admin.edit_project', id=id))

        project.title = title
        project.category = request.form.get('category', project.category).strip()
        project.short_description = request.form.get('short_description', '').strip()
        project.detailed_description = request.form.get('detailed_description', '').strip()
        
        image_url = convert_gdrive_url(request.form.get('image_url', '').strip())
        image_file = request.files.get('image_file')
        if image_file and image_file.filename != '':
            try:
                uploaded_url = save_uploaded_file(image_file)
                if uploaded_url:
                    delete_uploaded_file(project.image_url)
                    project.image_url = uploaded_url
            except Exception as ve:
                flash(str(ve), 'danger')
                return redirect(url_for('admin.edit_project', id=id))
        elif image_url:
            project.image_url = image_url

        project.github_url = request.form.get('github_url', '').strip()
        project.demo_url = request.form.get('demo_url', '').strip()
        project.tags = request.form.get('tags', '').strip()
        project.is_featured = True if request.form.get('is_featured') else False
        project.order_index = int(request.form.get('order_index', project.order_index))

        db.session.commit()
        flash(f'Project "{project.title}" updated successfully!', 'success')
        return redirect(url_for('admin.projects'))

    return render_template('admin/project_form.html', project=project)

@admin_bp.route('/projects/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    title = project.title
    delete_uploaded_file(project.image_url)
    db.session.delete(project)
    db.session.commit()
    flash(f'Project "{title}" removed.', 'info')
    return redirect(url_for('admin.projects'))

# --- RESEARCH & PUBLICATIONS MANAGEMENT ---
@admin_bp.route('/research')
@login_required
def research():
    all_research = Research.query.order_by(Research.order_index, Research.created_at.desc()).all()
    return render_template('admin/research.html', research_papers=all_research)

@admin_bp.route('/research/add', methods=['POST'])
@login_required
def add_research():
    title = request.form.get('title', '').strip()
    conference_or_journal = request.form.get('conference_or_journal', '').strip()
    publication_year = request.form.get('publication_year', '2026').strip()
    abstract = request.form.get('abstract', '').strip()
    paper_url = request.form.get('paper_url', '').strip()
    pdf_url = request.form.get('pdf_url', '').strip()
    tags = request.form.get('tags', '').strip()
    is_featured = True if request.form.get('is_featured') else False
    order_index = int(request.form.get('order_index', 0))

    if title and conference_or_journal:
        paper = Research(
            title=title,
            conference_or_journal=conference_or_journal,
            publication_year=publication_year,
            abstract=abstract,
            paper_url=paper_url,
            pdf_url=pdf_url,
            tags=tags,
            is_featured=is_featured,
            order_index=order_index
        )
        db.session.add(paper)
        db.session.commit()
        flash(f'Research paper "{title}" added successfully!', 'success')
    else:
        flash('Paper Title and Conference/Journal name are required.', 'danger')

    return redirect(url_for('admin.research'))

@admin_bp.route('/research/edit/<int:id>', methods=['POST'])
@login_required
def edit_research(id):
    paper = Research.query.get_or_404(id)
    paper.title = request.form.get('title', '').strip()
    paper.conference_or_journal = request.form.get('conference_or_journal', '').strip()
    paper.publication_year = request.form.get('publication_year', paper.publication_year).strip()
    paper.abstract = request.form.get('abstract', '').strip()
    paper.paper_url = request.form.get('paper_url', '').strip()
    paper.pdf_url = request.form.get('pdf_url', '').strip()
    paper.tags = request.form.get('tags', '').strip()
    paper.is_featured = True if request.form.get('is_featured') else False
    paper.order_index = int(request.form.get('order_index', paper.order_index))

    db.session.commit()
    flash(f'Research paper "{paper.title}" updated successfully!', 'success')
    return redirect(url_for('admin.research'))

@admin_bp.route('/research/delete/<int:id>', methods=['POST'])
@login_required
def delete_research(id):
    paper = Research.query.get_or_404(id)
    title = paper.title
    db.session.delete(paper)
    db.session.commit()
    flash(f'Research paper "{title}" removed.', 'info')
    return redirect(url_for('admin.research'))

# --- EXPERIENCE MANAGEMENT ---
@admin_bp.route('/experience')
@login_required
def experience():
    items = Experience.query.order_by(Experience.order_index, Experience.id.desc()).all()
    return render_template('admin/experience.html', items=items)

@admin_bp.route('/experience/add', methods=['POST'])
@login_required
def add_experience():
    type_val = request.form.get('type', 'work')
    title_or_degree = request.form.get('title_or_degree', '').strip()
    organization = request.form.get('organization', '').strip()
    location = request.form.get('location', '').strip()
    period = request.form.get('period', '').strip()
    is_current = True if request.form.get('is_current') else False
    description = request.form.get('description', '').strip()
    order_index = int(request.form.get('order_index', 0))

    if title_or_degree and organization:
        item = Experience(
            type=type_val,
            title_or_degree=title_or_degree,
            organization=organization,
            location=location,
            period=period,
            is_current=is_current,
            description=description,
            order_index=order_index
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Experience "{title_or_degree}" added successfully!', 'success')
    else:
        flash('Title/Degree and Organization/School are required.', 'danger')

    return redirect(url_for('admin.experience'))

@admin_bp.route('/experience/edit/<int:id>', methods=['POST'])
@login_required
def edit_experience(id):
    item = Experience.query.get_or_404(id)
    item.type = request.form.get('type', item.type)
    item.title_or_degree = request.form.get('title_or_degree', '').strip()
    item.organization = request.form.get('organization', '').strip()
    item.location = request.form.get('location', '').strip()
    item.period = request.form.get('period', '').strip()
    item.is_current = True if request.form.get('is_current') else False
    item.description = request.form.get('description', '').strip()
    item.order_index = int(request.form.get('order_index', item.order_index))

    db.session.commit()
    flash(f'Experience updated successfully!', 'success')
    return redirect(url_for('admin.experience'))

@admin_bp.route('/experience/delete/<int:id>', methods=['POST'])
@login_required
def delete_experience(id):
    item = Experience.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Experience record deleted.', 'info')
    return redirect(url_for('admin.experience'))

# --- DEDICATED MESSAGES INBOX & PAGE READER ---
@admin_bp.route('/messages')
@login_required
def messages():
    all_messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('admin/messages.html', messages=all_messages)

@admin_bp.route('/messages/<int:id>')
@login_required
def view_message(id):
    msg = Message.query.get_or_404(id)
    # Mark as read automatically when opening dedicated page
    if not msg.is_read:
        msg.is_read = True
        db.session.commit()
    return render_template('admin/message_detail.html', msg=msg)

@admin_bp.route('/messages/read/<int:id>', methods=['POST'])
@login_required
def toggle_message_read(id):
    msg = Message.query.get_or_404(id)
    msg.is_read = not msg.is_read
    db.session.commit()
    status = "read" if msg.is_read else "unread"
    flash(f'Message marked as {status}.', 'success')
    return redirect(request.referrer or url_for('admin.messages'))

@admin_bp.route('/messages/delete/<int:id>', methods=['POST'])
@login_required
def delete_message(id):
    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'info')
    return redirect(url_for('admin.messages'))

# --- SETTINGS & SECURITY ---
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            current_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')
            
            if not current_user.check_password(current_pwd):
                flash('Current password is incorrect.', 'danger')
            elif len(new_pwd) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
            elif new_pwd != confirm_pwd:
                flash('New passwords do not match.', 'danger')
            else:
                current_user.set_password(new_pwd)
                db.session.commit()
                flash('Your admin password has been updated successfully!', 'success')

    return render_template('admin/settings.html')

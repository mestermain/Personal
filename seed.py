from app import create_app
from models import db, AdminUser, SiteProfile, Skill, Project, Research, Experience, Message, SiteSetting

def seed_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # 1. Admin User
        admin = AdminUser.query.filter_by(username='admin').first()
        if not admin:
            admin = AdminUser(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("--> Seeded Admin User: admin / admin123")

        # 2. Site Profile
        profile = SiteProfile.query.first()
        if not profile:
            profile = SiteProfile(
                full_name="Talha Sadeeq",
                job_title="Machine Learning Engineer & Full-Stack Developer",
                hero_headline="Building High-Impact Web Applications & Intelligent AI Systems",
                hero_subheadline="Passionate software engineer specializing in Python, Machine Learning, Deep Learning, Flask backends, and modern responsive user interfaces.",
                about_summary="Crafting clean, responsive, and AI-driven applications from concept to deployment.",
                about_detailed="I am a dedicated software developer and AI engineer focused on building intelligent web applications, machine learning pipelines, scalable backends, and intuitive user interfaces. With extensive expertise in Python, Flask, PyTorch/TensorFlow, JavaScript, Bootstrap, and Tailwind CSS, I help turn complex ideas into high-performing software.",
                location="San Francisco, CA / Remote",
                email="talha@example.com",
                phone="+1 (555) 382-9102",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80",
                resume_url="#",
                github_url="https://github.com/talhasadeeq",
                linkedin_url="https://linkedin.com/in/talhasadeeq",
                leetcode_url="https://leetcode.com/u/talhasadeeq/",
                years_experience=6
            )
            db.session.add(profile)
            print("--> Seeded Site Profile")

        # 3. Skills with Dynamic Categories (Machine Learning & AI, Backend, Frontend, etc.)
        if Skill.query.count() == 0:
            skills_data = [
                # Machine Learning & AI
                ("Python & PyTorch", "Machine Learning & AI", 95, "fab fa-python", 1),
                ("Scikit-Learn & ML Algorithms", "Machine Learning & AI", 92, "fas fa-brain", 2),
                ("Computer Vision (OpenCV)", "Machine Learning & AI", 88, "fas fa-eye", 3),
                ("NLP & LLM Fine-tuning", "Machine Learning & AI", 85, "fas fa-robot", 4),

                # Backend
                ("Flask Framework", "Backend Development", 96, "fas fa-pepper-hot", 1),
                ("RESTful APIs & Microservices", "Backend Development", 94, "fas fa-network-wired", 2),
                ("Node.js", "Backend Development", 82, "fab fa-node-js", 3),

                # Frontend
                ("JavaScript (ES6+)", "Frontend Development", 95, "fab fa-js", 1),
                ("Tailwind CSS", "Frontend Development", 94, "fas fa-code", 2),
                ("Bootstrap 5", "Frontend Development", 95, "fab fa-bootstrap", 3),
                
                # Database & Cloud
                ("SQLite / PostgreSQL", "Database & Cloud", 90, "fas fa-database", 1),
                ("SQLAlchemy ORM", "Database & Cloud", 92, "fas fa-project-diagram", 2),
                ("Git & Docker", "Database & Cloud", 90, "fab fa-docker", 3),
            ]
            for name, cat, prof, icon, order in skills_data:
                db.session.add(Skill(name=name, category=cat, proficiency=prof, icon_class=icon, order_index=order))
            print("--> Seeded Skills with Machine Learning & AI Categories")

        # 4. Projects
        if Project.query.count() == 0:
            projects_data = [
                {
                    "title": "Smart Analytics & ML Dashboard",
                    "slug": "smart-analytics-ml-dashboard",
                    "category": "AI & Data",
                    "short_description": "An interactive real-time data visualization and machine learning inference platform built with Flask, PyTorch, and Tailwind CSS.",
                    "detailed_description": "Smart Analytics Dashboard empowers users to run machine learning predictions, visualize real-time time series metrics, and generate automated insights. Built with Flask, PyTorch, SQLite, and Chart.js.",
                    "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80",
                    "github_url": "https://github.com",
                    "demo_url": "https://example.com",
                    "tags": "Python, Flask, PyTorch, Tailwind CSS, Chart.js",
                    "is_featured": True,
                    "order_index": 1
                },
                {
                    "title": "E-Commerce CMS Platform",
                    "slug": "e-commerce-cms-platform",
                    "category": "Web Application",
                    "short_description": "Comprehensive online shop engine featuring product catalog management, order tracking, and payment gateway integration.",
                    "detailed_description": "Full-fledged e-commerce platform built with Flask and Bootstrap 5. Includes customer authentication, shopping cart, admin inventory control, and stripe payment flow.",
                    "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
                    "github_url": "https://github.com",
                    "demo_url": "https://example.com",
                    "tags": "Flask, Bootstrap 5, SQLite, Stripe API",
                    "is_featured": True,
                    "order_index": 2
                }
            ]
            for p in projects_data:
                db.session.add(Project(**p))
            print("--> Seeded Projects")

        # 5. Research Papers
        if Research.query.count() == 0:
            research_data = [
                {
                    "title": "Optimizing Neural Network Architectures for Edge Devices",
                    "conference_or_journal": "IEEE International Conference on Artificial Intelligence",
                    "publication_year": "2025",
                    "abstract": "This research explores lightweight deep neural network model quantization and pruning techniques to achieve high inference accuracy with minimal latency on resource-constrained embedded systems.",
                    "paper_url": "https://arxiv.org",
                    "pdf_url": "https://arxiv.org",
                    "tags": "Machine Learning, Model Quantization, Computer Vision",
                    "is_featured": True,
                    "order_index": 1
                },
                {
                    "title": "Real-Time Anomaly Detection in High-Dimensional Time Series",
                    "conference_or_journal": "Journal of Machine Learning Research (JMLR)",
                    "publication_year": "2024",
                    "abstract": "We present a unsupervised Transformer-based framework for detecting anomalies in industrial sensor streams. Experimental evaluation shows superior F1-score performance compared to traditional autoencoders.",
                    "paper_url": "https://arxiv.org",
                    "pdf_url": "https://arxiv.org",
                    "tags": "Transformers, Time Series, Anomaly Detection",
                    "is_featured": True,
                    "order_index": 2
                }
            ]
            for r in research_data:
                db.session.add(Research(**r))
            print("--> Seeded Research Papers")

        # 6. Experience & Education
        if Experience.query.count() == 0:
            exp_data = [
                {
                    "type": "work",
                    "title_or_degree": "Senior Full-Stack & ML Engineer",
                    "organization": "Apex Software Solutions",
                    "location": "San Francisco, CA",
                    "period": "2023 - Present",
                    "is_current": True,
                    "description": "Lead the development of cloud-hosted web applications and machine learning services using Flask, PyTorch, and modern frontend frameworks. Direct architecture, model training, and performance optimizations.",
                    "order_index": 1
                },
                {
                    "type": "education",
                    "title_or_degree": "B.S. in Computer Science & AI",
                    "organization": "State University of Technology",
                    "location": "San Francisco, CA",
                    "period": "2017 - 2021",
                    "is_current": False,
                    "description": "Graduated with Honors. Specialized in Artificial Intelligence, Machine Learning, Computer Vision, and Software Engineering.",
                    "order_index": 2
                }
            ]
            for e in exp_data:
                db.session.add(Experience(**e))
            print("--> Seeded Work & Education Experience")

        # 7. Initial Sample Message
        if Message.query.count() == 0:
            db.session.add(Message(
                sender_name="Sarah Jenkins",
                sender_email="sarah.j@techinnovations.io",
                subject="Inquiry regarding Machine Learning & Flask Project",
                message_body="Hi Talha, I came across your portfolio website and was really impressed by your work on Flask web applications and Machine Learning models. We have an upcoming project and would love to connect!",
                is_read=False
            ))
            print("--> Seeded Initial Message")

        db.session.commit()
        print("--> Database Seeding Complete!")

if __name__ == '__main__':
    seed_database()

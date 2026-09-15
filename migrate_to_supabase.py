import sys
import os
from sqlalchemy import create_engine
from app import create_app
from models import db, AdminUser, SiteProfile, Skill, Project, Research, Experience, Message, SiteSetting

def migrate(supabase_db_url):
    if supabase_db_url.startswith("postgres://"):
        supabase_db_url = supabase_db_url.replace("postgres://", "postgresql://", 1)

    print(f"Connecting to Supabase Database...")
    
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = supabase_db_url

    with app.app_context():
        print("1. Creating database tables in Supabase...")
        db.create_all()

        # Connect to local SQLite to read existing data
        sqlite_path = os.path.join(app.root_path, 'instance', 'personal_web.db')
        sqlite_uri = f'sqlite:///{sqlite_path}'
        sqlite_engine = create_engine(sqlite_uri)

        print("2. Migrating records from local SQLite...")

        # Copy Admin Users
        with sqlite_engine.connect() as conn:
            from sqlalchemy.orm import sessionmaker
            LocalSession = sessionmaker(bind=sqlite_engine)
            local_session = LocalSession()

            profiles = local_session.query(SiteProfile).all()
            for p in profiles:
                local_session.expunge(p)
                db.session.merge(p)

            users = local_session.query(AdminUser).all()
            for u in users:
                local_session.expunge(u)
                db.session.merge(u)

            skills = local_session.query(Skill).all()
            for s in skills:
                local_session.expunge(s)
                db.session.merge(s)

            projects = local_session.query(Project).all()
            for prj in projects:
                local_session.expunge(prj)
                db.session.merge(prj)

            papers = local_session.query(Research).all()
            for r in papers:
                local_session.expunge(r)
                db.session.merge(r)

            exps = local_session.query(Experience).all()
            for ex in exps:
                local_session.expunge(ex)
                db.session.merge(ex)

            msgs = local_session.query(Message).all()
            for m in msgs:
                local_session.expunge(m)
                db.session.merge(m)

            db.session.commit()
            local_session.close()

        print("SUCCESS: Migration to Supabase database completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_supabase.py '<YOUR_SUPABASE_DATABASE_URL>'")
        sys.exit(1)
    
    migrate(sys.argv[1])

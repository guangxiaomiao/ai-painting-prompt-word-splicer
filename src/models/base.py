from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_app_dir()
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'prompt_db.sqlite')

engine = create_engine(f'sqlite:///{DATABASE_PATH}', connect_args={'check_same_thread': False})
SessionFactory = sessionmaker(bind=engine)
Base = declarative_base()

def get_session():
    return SessionFactory()

def init_db():
    from .category import Category
    from .prompt import Prompt
    from .template import Template
    from .random_rule import RandomRule
    from .settings import Settings

    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    Base.metadata.create_all(engine)

    migrate_db()

    session = get_session()
    if not session.query(Settings).first():
        default_settings = Settings()
        session.add(default_settings)
        session.commit()
    session.close()

def migrate_db():
    from sqlalchemy import text, inspect
    inspector = inspect(engine)

    with engine.connect() as conn:
        if 'settings' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('settings')]

            if 'ollama_enabled' not in columns:
                try:
                    conn.execute(text("ALTER TABLE settings ADD COLUMN ollama_enabled BOOLEAN DEFAULT 0"))
                    conn.commit()
                except Exception:
                    pass

            if 'ollama_base_url' not in columns:
                try:
                    conn.execute(text("ALTER TABLE settings ADD COLUMN ollama_base_url VARCHAR(200) DEFAULT 'http://localhost:11434'"))
                    conn.commit()
                except Exception:
                    pass

            if 'ollama_model' not in columns:
                try:
                    conn.execute(text("ALTER TABLE settings ADD COLUMN ollama_model VARCHAR(200) DEFAULT ''"))
                    conn.commit()
                except Exception:
                    pass

        if 'prompts' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('prompts')]

            if 'prompt_type' not in columns:
                try:
                    conn.execute(text("ALTER TABLE prompts ADD COLUMN prompt_type VARCHAR(20) DEFAULT 'positive'"))
                    conn.commit()
                except Exception:
                    pass

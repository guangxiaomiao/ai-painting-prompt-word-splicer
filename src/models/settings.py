from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from .base import Base
from datetime import datetime

class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    theme = Column(String(50), default='dark')
    font_size = Column(Integer, default=12)
    language = Column(String(20), default='zh')
    auto_save = Column(Boolean, default=True)
    auto_backup = Column(Boolean, default=True)
    backup_interval = Column(Integer, default=24)
    default_output_format = Column(String(20), default='english')
    show_mode = Column(String(20), default='english')
    ollama_enabled = Column(Boolean, default=False)
    ollama_base_url = Column(String(200), default='http://localhost:11434')
    ollama_model = Column(String(200), default='')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'theme': self.theme,
            'font_size': self.font_size,
            'language': self.language,
            'auto_save': self.auto_save,
            'auto_backup': self.auto_backup,
            'backup_interval': self.backup_interval,
            'default_output_format': self.default_output_format,
            'show_mode': self.show_mode,
            'ollama_enabled': self.ollama_enabled,
            'ollama_base_url': self.ollama_base_url,
            'ollama_model': self.ollama_model,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def update_from_dict(self, data):
        if 'theme' in data:
            self.theme = data['theme']
        if 'font_size' in data:
            self.font_size = data['font_size']
        if 'language' in data:
            self.language = data['language']
        if 'auto_save' in data:
            self.auto_save = data['auto_save']
        if 'auto_backup' in data:
            self.auto_backup = data['auto_backup']
        if 'backup_interval' in data:
            self.backup_interval = data['backup_interval']
        if 'default_output_format' in data:
            self.default_output_format = data['default_output_format']
        if 'show_mode' in data:
            self.show_mode = data['show_mode']
        if 'ollama_enabled' in data:
            self.ollama_enabled = data['ollama_enabled']
        if 'ollama_base_url' in data:
            self.ollama_base_url = data['ollama_base_url']
        if 'ollama_model' in data:
            self.ollama_model = data['ollama_model']

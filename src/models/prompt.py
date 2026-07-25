from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True)
    english = Column(String(500), nullable=False)
    chinese = Column(String(500))
    note = Column(Text)
    aliases = Column(String(1000))
    tags = Column(String(1000))
    weight = Column(Float, default=1.0)
    prompt_type = Column(String(20), default='positive')  # 'positive' 或 'negative'
    enabled = Column(Boolean, default=True)
    favorite = Column(Boolean, default=False)
    probability = Column(Float, default=1.0)
    random_weight = Column(Float, default=1.0)
    author = Column(String(100))
    source = Column(String(200))
    version = Column(String(50))
    category_id = Column(Integer, ForeignKey('categories.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    category = relationship('Category', back_populates='prompts')
    template_items = relationship('TemplateItem', back_populates='prompt')

    def to_dict(self):
        return {
            'id': self.id,
            'english': self.english,
            'chinese': self.chinese,
            'note': self.note,
            'aliases': self.aliases,
            'tags': self.tags,
            'weight': self.weight if self.weight is not None else 1.0,
            'prompt_type': self.prompt_type if self.prompt_type is not None else 'positive',
            'enabled': self.enabled,
            'favorite': self.favorite,
            'probability': self.probability,
            'random_weight': self.random_weight,
            'author': self.author,
            'source': self.source,
            'version': self.version,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            english=data.get('english'),
            chinese=data.get('chinese'),
            note=data.get('note'),
            aliases=data.get('aliases'),
            tags=data.get('tags'),
            weight=data.get('weight', 1.0),
            prompt_type=data.get('prompt_type', 'positive'),
            enabled=data.get('enabled', True),
            favorite=data.get('favorite', False),
            probability=data.get('probability', 1.0),
            random_weight=data.get('random_weight', 1.0),
            author=data.get('author'),
            source=data.get('source'),
            version=data.get('version'),
            category_id=data.get('category_id')
        )

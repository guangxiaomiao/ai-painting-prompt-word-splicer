from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    name_cn = Column(String(100))
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    items = relationship('TemplateItem', back_populates='template', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_cn': self.name_cn,
            'description': self.description,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data):
        template = cls(
            name=data.get('name'),
            name_cn=data.get('name_cn'),
            description=data.get('description'),
            enabled=data.get('enabled', True)
        )
        return template

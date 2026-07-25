from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class TemplateItem(Base):
    __tablename__ = 'template_items'
    
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('templates.id'))
    prompt_id = Column(Integer, ForeignKey('prompts.id'))
    order = Column(Integer, default=0)
    weight = Column(Integer)
    enabled = Column(Boolean, default=True)
    
    template = relationship('Template', back_populates='items')
    prompt = relationship('Prompt', back_populates='template_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'prompt_id': self.prompt_id,
            'order': self.order,
            'weight': self.weight,
            'enabled': self.enabled
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            template_id=data.get('template_id'),
            prompt_id=data.get('prompt_id'),
            order=data.get('order', 0),
            weight=data.get('weight'),
            enabled=data.get('enabled', True)
        )

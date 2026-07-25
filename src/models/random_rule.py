from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class RandomRule(Base):
    __tablename__ = 'random_rules'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    mode = Column(String(20), default='optional')
    min_count = Column(Integer, default=0)
    max_count = Column(Integer, default=1)
    probability = Column(Float, default=1.0)
    use_weight = Column(Boolean, default=True)
    
    category = relationship('Category', back_populates='random_rule')
    
    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'mode': self.mode,
            'min_count': self.min_count,
            'max_count': self.max_count,
            'probability': self.probability,
            'use_weight': self.use_weight
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            category_id=data.get('category_id'),
            mode=data.get('mode', 'optional'),
            min_count=data.get('min_count', 0),
            max_count=data.get('max_count', 1),
            probability=data.get('probability', 1.0),
            use_weight=data.get('use_weight', True)
        )

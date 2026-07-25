from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    name_cn = Column(String(100))
    parent_id = Column(Integer, ForeignKey('categories.id'))
    order = Column(Integer, default=0)
    expanded = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    parent = relationship('Category', remote_side=[id], back_populates='children')
    children = relationship('Category', back_populates='parent')
    prompts = relationship('Prompt', back_populates='category', cascade='all, delete-orphan')
    random_rule = relationship('RandomRule', uselist=False, back_populates='category')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_cn': self.name_cn,
            'parent_id': self.parent_id,
            'order': self.order,
            'expanded': self.expanded,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name'),
            name_cn=data.get('name_cn'),
            parent_id=data.get('parent_id'),
            order=data.get('order', 0),
            expanded=data.get('expanded', True),
            enabled=data.get('enabled', True)
        )

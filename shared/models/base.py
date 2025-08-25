from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr, declarative_base

Base = declarative_base()

class BaseModel:
    """Base model class that includes common fields and methods."""
    
    # This will be set by SQLAlchemy when the instance is created
    id = None
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def __tablename__(cls):
        ""
        Generate table name automatically from class name.
        Converts CamelCase class names to snake_case table names.
        """
        return ''.join(['_' + i.lower() if i.isupper() else i for i in cls.__name__]).lstrip('_')
    
    def to_dict(self):
        ""Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            result[column.name] = getattr(self, column.name)
        return result
    
    def update(self, **kwargs):
        ""Update model instance with given attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

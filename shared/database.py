import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from .config import Config

class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        ""Initialize the database connection and session factory."""
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), Config.DB_NAME)
        db_url = f"sqlite:///{db_path}"
        
        self._engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
        )
    
    @property
    def engine(self):
        ""Get the SQLAlchemy engine."""
        if self._engine is None:
            self._initialize()
        return self._engine
    
    @property
    def session(self):
        ""Get a new database session."""
        if self._session_factory is None:
            self._initialize()
        return self._session_factory()
    
    @contextmanager
    def session_scope(self):
        ""Provide a transactional scope around a series of operations."""
        session = self.session
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_tables(self):
        ""Create all database tables."""
        from .models.base import Base
        from .models.core import User, Restaurant, Waiter, Tab, MenuItem, Order, OrderItem, Payment, Message
        
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        ""Drop all database tables. Use with caution!"""
        from .models.base import Base
        
        Base.metadata.drop_all(bind=self.engine)

# Singleton instance
db = DatabaseManager()

# Alias for easier access
SessionLocal = db.session

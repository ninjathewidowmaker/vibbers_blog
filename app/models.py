from sqlalchemy import Column, Integer, String, Text, Index, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Blog(Base):
    __tablename__ = "blog"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(500), nullable=False, unique=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(Text), server_default="{}")
    image_urls = Column(ARRAY(Text), server_default="{}")
    author = Column(String(100), server_default="Your Name")
    views = Column(Integer, nullable=False, default=0)
    template = Column(Integer, nullable=False, default=1)
    is_blog = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now)

    __table_args__ = (
        Index('idx_blog_tags', 'tags', postgresql_using='gin'),
    )
    



class Template(Base):
    __tablename__ = "template"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False, unique=True)
    page = Column(Text, nullable = False)
    description = Column(String)
        
        
class User(Base):
    __tablename__ = "user"
    
    id - Column(Integer, primary_key = True, autoincrement = True)
    username = Column(String(50), nullable = False, unique = True)
    email = Column(String(255), nullable = False, unique = True)
    hashed_password = Column(String(255), nullable = False)
    role = Column(String(250), nullable = False)
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime(timezone = True), default = datetime.datetime.now)
    
    
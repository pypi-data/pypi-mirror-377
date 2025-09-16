#!/usr/bin/env python3
"""
Example: SQLAlchemy Models for dbPorter

This example shows how to create a proper models.py file that dbPorter can use
for auto-generating migrations. The key requirement is that the file must have
a 'metadata' or 'MetaData' object that contains your SQLAlchemy table definitions.

Usage:
1. Copy this file to your project as 'models.py'
2. Modify the table definitions to match your schema
3. Run: dbporter autogenerate -m "Your migration message"
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create the declarative base
Base = declarative_base()

# dbPorter will automatically detect Base.metadata
# No need to create a separate metadata object when using declarative base

# Example User table
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Example Post table
class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    author_id = Column(Integer, nullable=False)  # Foreign key to users.id
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Example Category table
class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Alternative approach: Define tables directly with metadata
# This is useful if you prefer not to use the declarative base
"""
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, Text, MetaData

# Create metadata object for direct table definitions
metadata = MetaData()

users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(80), unique=True, nullable=False),
    Column('email', String(120), unique=True, nullable=False),
    Column('password_hash', String(255), nullable=False),
    Column('is_active', Boolean, default=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

posts_table = Table('posts', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(200), nullable=False),
    Column('content', Text, nullable=True),
    Column('author_id', Integer, nullable=False),
    Column('is_published', Boolean, default=False),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)
"""

# Important: dbPorter will automatically detect:
# - Base.metadata (when using declarative base - RECOMMENDED)
# - metadata (when using direct table definitions)
# - MetaData (alternative naming)

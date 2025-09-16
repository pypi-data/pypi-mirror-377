#!/usr/bin/env python3
"""
Minimal Example: SQLAlchemy Models for dbPorter

This is the simplest possible models.py file that dbPorter can use.
It shows the absolute minimum requirements.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base
Base = declarative_base()

# Example: Simple User table
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

# That's it! dbPorter will automatically detect Base.metadata
# No need to create a separate metadata object when using declarative base

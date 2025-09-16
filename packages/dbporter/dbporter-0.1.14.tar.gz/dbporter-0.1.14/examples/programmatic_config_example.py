#!/usr/bin/env python3
"""
Example: Programmatic Database Configuration

This example shows how to use the migration tool with programmatic configuration
for security-conscious organizations that don't want to store credentials in files.
"""

import os
import sys

# Add the parent directory to the path so we can import the migration tool
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dbPorter import set_database_url, get_database_url

def main():
    """
    Example of setting database URL programmatically.
    
    This approach is ideal for:
    - Security-conscious organizations
    - CI/CD environments where credentials are in environment variables
    - Applications that already have database configuration
    - Multi-tenant applications with dynamic database URLs
    """
    
    # Method 1: Direct URL (most common)
    db_url = "postgresql://user:password@localhost:5432/mydatabase"
    set_database_url(db_url)
    
    # Method 2: From environment variables (recommended for production)
    # db_url = os.getenv("DATABASE_URL")
    # if db_url:
    #     set_database_url(db_url)
    # else:
    #     raise ValueError("DATABASE_URL environment variable not set")
    
    # Method 3: From application configuration
    # from myapp.config import get_database_url
    # db_url = get_database_url()
    # set_database_url(db_url)
    
    # Method 4: Dynamic construction
    # host = os.getenv("DB_HOST", "localhost")
    # port = os.getenv("DB_PORT", "5432")
    # user = os.getenv("DB_USER")
    # password = os.getenv("DB_PASSWORD")
    # database = os.getenv("DB_NAME")
    # 
    # if all([user, password, database]):
    #     db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    #     set_database_url(db_url)
    # else:
    #     raise ValueError("Required database environment variables not set")
    
    print("✅ Database URL set programmatically!")
    print("Non-sensitive configuration saved to migrate_config.json")
    
    # Verify the configuration was set
    retrieved_url = get_database_url()
    print(f"🔍 Retrieved URL: {retrieved_url}")
    
    print("\n💡 For CLI commands, use one of these methods:")
    print("  1. Environment variables:")
    print("     export DBPORTER_DATABASE_URL='postgresql://user:pass@host:port/db'")
    print("  2. Command line arguments:")
    print("     python main.py status --db 'postgresql://user:pass@host:port/db'")
    print("  3. Use the saved configuration (non-sensitive data only)")
    
    print("\n💡 Programmatic configuration functions:")
    print("  - get_database_url(): Retrieve the currently set URL (current process only)")
    print("  - set_database_url(): Set database URL programmatically")

if __name__ == "__main__":
    main()

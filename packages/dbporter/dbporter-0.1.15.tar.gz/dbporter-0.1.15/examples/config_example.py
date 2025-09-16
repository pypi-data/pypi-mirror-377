"""
Example config.py file showing how dbPorter can automatically detect database URLs.

dbPorter will automatically find and use the database URL from this file without
any additional configuration. Just add one of these patterns to your config.py.
"""

# Option 1: Simple variable assignment
DATABASE_URL = "postgresql://user:password@localhost/mydb"

# Option 2: Alternative variable names (all supported)
# DB_URL = "postgresql://user:password@localhost/mydb"
# database_url = "postgresql://user:password@localhost/mydb"
# db_url = "postgresql://user:password@localhost/mydb"
# DB_STRING = "postgresql://user:password@localhost/mydb"
# db_string = "postgresql://user:password@localhost/mydb"

# Option 3: Function that returns database URL
def get_database_url():
    """Return the database URL for the current environment."""
    import os
    
    # Check environment first
    if url := os.getenv('DATABASE_URL'):
        return url
    
    # Fall back to default
    return "postgresql://user:password@localhost/mydb"

# Option 4: Alternative function names (all supported)
# def get_db_url():
#     return "postgresql://user:password@localhost/mydb"
# 
# def database_url():
#     return "postgresql://user:password@localhost/mydb"
# 
# def db_url():
#     return "postgresql://user:password@localhost/mydb"

# Option 5: Environment-specific configuration
def get_database_url_by_env():
    """Return database URL based on environment."""
    import os
    
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        return "postgresql://prod_user:prod_pass@prod_host:5432/prod_db"
    elif env == 'staging':
        return "postgresql://staging_user:staging_pass@staging_host:5432/staging_db"
    else:
        return "postgresql://dev_user:dev_pass@localhost:5432/dev_db"

# Option 6: Dynamic configuration with secrets
def get_database_url_with_secrets():
    """Return database URL with secrets from environment."""
    import os
    
    # Get individual components from environment
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER', 'myuser')
    password = os.getenv('DB_PASSWORD', 'mypassword')
    database = os.getenv('DB_NAME', 'mydb')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

# Option 7: Class-based configuration
class DatabaseConfig:
    def __init__(self):
        self.host = "localhost"
        self.port = 5432
        self.user = "myuser"
        self.password = "mypassword"
        self.database = "mydb"
    
    def get_url(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

# Create instance for dbPorter to find
db_config = DatabaseConfig()

# Option 8: Multiple database support
def get_primary_database_url():
    """Return URL for primary database."""
    return "postgresql://user:password@localhost/primary_db"

def get_secondary_database_url():
    """Return URL for secondary database."""
    return "postgresql://user:password@localhost/secondary_db"

# dbPorter will use the first one it finds

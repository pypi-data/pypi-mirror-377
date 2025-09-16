"""
Simple config.py example showing how dbPorter automatically detects database URLs.

Just add ONE of these patterns to your config.py file, and dbPorter will
automatically use it without any additional configuration.
"""

# Option 1: Simple variable (most common)
DATABASE_URL = "postgresql://user:password@localhost/mydb"

# Option 2: Alternative variable names
# DB_URL = "postgresql://user:password@localhost/mydb"
# database_url = "postgresql://user:password@localhost/mydb"
# db_url = "postgresql://user:password@localhost/mydb"

# Option 3: Function that returns URL
# def get_database_url():
#     return "postgresql://user:password@localhost/mydb"

# Option 4: Environment-specific function
# def get_database_url():
#     import os
#     env = os.getenv('ENVIRONMENT', 'development')
#     
#     if env == 'production':
#         return "postgresql://prod_user:prod_pass@prod_host:5432/prod_db"
#     else:
#         return "postgresql://dev_user:dev_pass@localhost:5432/dev_db"

# That's it! dbPorter will automatically find and use this database URL.
# No need to store it in separate files or set environment variables.

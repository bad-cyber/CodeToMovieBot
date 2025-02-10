import os

# Get the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database paths
DATABASE_DIR = os.path.join(ROOT_DIR, 'database')
DATABASE_FILE = os.path.join(DATABASE_DIR, 'sqlitebot.db')

# Config paths
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')
ADMINS_FILE = os.path.join(CONFIG_DIR, 'admins.txt')

# Ensure directories exist
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Export paths
__all__ = ['ROOT_DIR', 'DATABASE_DIR', 'DATABASE_FILE', 'CONFIG_DIR', 'ADMINS_FILE']

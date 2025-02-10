"""
Database module for the Telegram Film Bot.
Contains database connection and operations.
"""

from .db import DB

__all__ = ['DB']

# Database schema version
DB_VERSION = '1.0'

# Table schemas
TABLES = {
    'users': '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER UNIQUE NOT NULL
        )
    ''',
    'films': '''
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key INTEGER UNIQUE NOT NULL,
            img_id TEXT NOT NULL,
            name TEXT NOT NULL,
            duration TEXT NOT NULL,
            score TEXT NOT NULL,
            genre TEXT NOT NULL,
            year TEXT NOT NULL,
            country TEXT NOT NULL,
            desc TEXT NOT NULL
        )
    '''
}

# Indexes
INDEXES = {
    'films_key_idx': 'CREATE INDEX IF NOT EXISTS films_key_idx ON films(key)',
    'users_userid_idx': 'CREATE INDEX IF NOT EXISTS users_userid_idx ON users(userid)'
}

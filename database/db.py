import sqlite3
import logging
from config.paths import DATABASE_FILE

class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()
        self._ensure_tables()

    def _ensure_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Create users table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userid INTEGER UNIQUE NOT NULL
                )
            """)

            # Create films table
            self.cursor.execute("""
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
            """)

            self.conn.commit()
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {e}")
            raise

    def add_user(self, userid):
        try:
            self.cursor.execute("INSERT INTO 'users' ('userid') VALUES (?)", (userid,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # User already exists
            return True
        except Exception as e:
            logging.error(f"Error adding user: {e}")
            return False

    def add_film(self, key, img_id, name, duration, score, genre, year, country, desc):
        try:
            self.cursor.execute("""
                INSERT INTO 'films' 
                ('key', 'img_id', 'name', 'duration', 'score', 'genre', 'year', 'country', 'desc') 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (key, img_id, name, duration, score, genre, year, country, desc))
            self.conn.commit()
            logging.info(f'New film #{key} has been successfully added to database!')
            return True
        except Exception as e:
            logging.error(f"Error adding film: {e}")
            return False

    def get_user(self, userid):
        try:
            result = self.cursor.execute("SELECT * FROM 'users' WHERE userid=?", (userid,))
            return result.fetchone()
        except Exception as e:
            logging.error(f"Error retrieving user: {e}")
            return None

    def get_film(self, key):
        try:
            film = self.cursor.execute("SELECT * FROM 'films' WHERE key=?", (key,))
            return film.fetchone()
        except Exception as e:
            logging.error(f"Error retrieving film: {e}")
            return None

    def delete_film(self, key):
        try:
            self.cursor.execute("DELETE FROM 'films' WHERE key=?", (key,))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error deleting film: {str(e)}")
            return False

    def get_randfilm(self):
        try:
            random_film = self.cursor.execute("SELECT * FROM 'films' ORDER BY RANDOM() LIMIT 1")
            return random_film.fetchone()
        except Exception as e:
            logging.error(f"Error retrieving random film: {e}")
            return None

    def get_keysfilms(self):
        try:
            all_films = self.cursor.execute("SELECT * from 'films'")
            return all_films.fetchall()
        except Exception as e:
            logging.error(f"Error retrieving all films: {e}")
            return []

    def update_film(self, code, field, value):
        field_map = {
            "name": "name",
            "desc": "desc",
            "genre": "genre",
            "year": "year",
            "country": "country",
            "image": "img_id"
        }
        
        if field not in field_map:
            raise ValueError(f"Неверное поле для обновления: {field}")
            
        db_field = field_map[field]
        try:
            self.cursor.execute(f"UPDATE films SET {db_field} = ? WHERE key = ?", (value, code))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating film: {str(e)}")
            return False

    def close(self):
        """Close the database connection"""
        try:
            self.conn.close()
            logging.info("Database connection closed")
        except Exception as e:
            logging.error(f"Error closing database connection: {e}")

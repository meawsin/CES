import pymysql
from pymysql.cursors import DictCursor
from pymysql import Error
from config import DATABASE_CONFIG

class DBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        """Establishes a database connection using PyMySQL."""
        if self.connection is None:
            try:
                # Add the cursorclass directly to the connection arguments
                db_config_with_cursor = DATABASE_CONFIG.copy()
                db_config_with_cursor['cursorclass'] = DictCursor
                self.connection = pymysql.connect(**db_config_with_cursor)
                print("Successfully connected to the database using PyMySQL.")
            except Error as e:
                print(f"Error connecting to MySQL database with PyMySQL: {e}")
                self.connection = None
        return self.connection

    def disconnect(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
            self.connection = None

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Executes a SQL query and returns results if any."""
        self.connect()
        if not self.connection:
            return None

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()

            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return True
        except Error as e:
            print(f"Error executing query: {query}\nError: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def fetch_data(self, query, params=None, fetch_one=False, fetch_all=True):
        """Helper for SELECT queries that return dictionaries."""
        self.connect()
        if not self.connection:
            return None

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return None
        except Error as e:
            print(f"Error fetching data: {query}\nError: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

if __name__ == "__main__":
    db = DBManager()
    if db.connect():
        print("Test connection successful!")
    db.disconnect()
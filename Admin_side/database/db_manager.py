import mysql.connector
from mysql.connector import Error
from config import DATABASE_CONFIG

class DBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        """Establishes a database connection."""
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(**DATABASE_CONFIG)
                if self.connection.is_connected():
                    print("Successfully connected to the database.")
            except Error as e:
                print(f"Error connecting to MySQL database: {e}")
                self.connection = None
        return self.connection

    def disconnect(self):
        """Closes the database connection."""
        if self.connection and self.connection.is_connected():
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
            cursor = self.connection.cursor(buffered=True)
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
        """Helper for SELECT queries."""
        self.connect()
        if not self.connection:
            return None

        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
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
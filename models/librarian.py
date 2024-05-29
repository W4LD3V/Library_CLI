import sqlite3  # Import the sqlite3 module to interact with SQLite databases

class Librarian:
    def __init__(self, username, password, fullname):
        # Constructor to initialize the Librarian object with a username, password, and fullname
        self.username = username
        self.password = password
        self.fullname = fullname

    def save(self, conn):
        # Method to save the librarian details into the database
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            INSERT INTO Librarian (Username, Password, FullName)
            VALUES (?, ?, ?)
        ''', (self.username, self.password, self.fullname))  # Execute the SQL query to insert librarian details
        conn.commit()  # Commit the transaction to save changes to the database

    @staticmethod
    def authenticate(conn, username, password):
        # Static method to authenticate a librarian using their username and password
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT * FROM Librarian WHERE Username=? AND Password=?
        ''', (username, password))  # Execute the SQL query to select a librarian with matching username and password
        return cursor.fetchone()  # Fetch and return the result of the query (None if no match found)

import sqlite3  # Imports the sqlite3 module to interact with SQLite databases
from datetime import datetime  # Imports the datetime class from the datetime module
from tabulate import tabulate  # Imports the tabulate function to format tables in the console

from utils.utils import add_one_month, add_one_year  # Imports utility functions from the utils module
from models import Librarian, User, Book, Rental  # Imports model classes from the models module

class Library:
    def __init__(self, db_name='library.db'):
        # Initialize the Library class, connecting to the SQLite database
        self.conn = sqlite3.connect(db_name)
        self.create_tables()  # Create the necessary tables if they don't exist

    def create_tables(self):
        # Method to create tables in the database
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                LibraryCardNumber TEXT UNIQUE NOT NULL,
                FullName TEXT NOT NULL,
                ValidUntil DATE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Librarian (
                LibrarianID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                FullName TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Book (
                BookID INTEGER PRIMARY KEY AUTOINCREMENT,
                Title TEXT,
                Author TEXT,
                Year INTEGER,
                Genre TEXT,
                ISBN TEXT NOT NULL,
                Count INTEGER DEFAULT 1
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Rental (
                RentalID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                BookID INTEGER NOT NULL,
                RentalDate DATE NOT NULL DEFAULT (date('now')),
                ReturnDate DATE NOT NULL,
                Returned BOOLEAN DEFAULT 0,
                Quantity INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (UserID) REFERENCES User (UserID),
                FOREIGN KEY (BookID) REFERENCES Book (BookID)
            )
        ''')
        self.conn.commit()  # Commit the changes to the database

    def insert_sample_data(self):
        # Method to insert sample data into the database for testing purposes
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Librarian")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO Librarian (Username, Password, FullName) VALUES
                ('admin1', 'password1', 'Librarian One'),
                ('admin2', 'password2', 'Librarian Two')
            ''')

        cursor.execute("SELECT COUNT(*) FROM User")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO User (LibraryCardNumber, FullName, ValidUntil) VALUES
                ('CARD12345', 'User One', '2025-12-31'),
                ('CARD67890', 'User Two', '2024-12-31')
            ''')

        cursor.execute("SELECT COUNT(*) FROM Book")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO Book (Title, Author, Year, Genre, ISBN, Count) VALUES
                ('Book One', 'Author One', 2001, 'Fiction', 'ISBN001', 5),
                ('Book Two', 'Author Two', 2015, 'Non-Fiction', 'ISBN002', 2)
            ''')

        cursor.execute("SELECT COUNT(*) FROM Rental")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO Rental (UserID, BookID, RentalDate, ReturnDate, Returned, Quantity) VALUES
                (1, 1, '2024-01-01', '2024-02-01', 0, 1),
                (2, 2, '2024-03-01', '2024-04-01', 0, 1)
            ''')

        self.conn.commit()  # Commit the changes to the database

    def add_librarian(self, username, password, fullname):
        # Method to add a new librarian to the database
        librarian = Librarian(username, password, fullname)
        librarian.save(self.conn)

    def authenticate_admin(self, username, password):
        # Method to authenticate an admin using username and password
        return Librarian.authenticate(self.conn, username, password)

    def authenticate_user(self, library_card_number):
        # Method to authenticate a user using their library card number
        return User.authenticate(self.conn, library_card_number)

    def register_user(self, full_name):
        # Method to register a new user and return their library card number
        user = User(full_name)
        user.save(self.conn)
        return user.library_card_number

    def add_book(self, title, author, year, genre, isbn, count):
        # Method to add a new book to the library
        book = Book(title, author, year, genre, isbn, count)
        book.save(self.conn)

    def delete_book_by_isbn(self, isbn, count_to_delete=None):
        # Method to delete a book by its ISBN and optionally a specific count
        Book.delete_by_isbn(self.conn, isbn, count_to_delete)

    def delete_book_by_year(self, year):
        # Method to delete books published in or before a specific year
        Book.delete_by_year(self.conn, year)

    def rent_book(self, library_card_number, isbn, return_date, quantity):
        # Method to rent a book to a user
        user = User.get_by_library_card(self.conn, library_card_number)
        if user:
            if not user.has_overdue_books(self.conn):
                rental = Rental(user.user_id, isbn, return_date, quantity)
                rental.save(self.conn)
            else:
                print("User has overdue books and cannot rent new books.")
        else:
            print("User not found.")

    def check_rental_status(self, library_card_number):
        # Method to check if a user has any overdue rentals
        return User.check_rental_status(self.conn, library_card_number)

    def return_book(self, library_card_number, isbn, quantity=None):
        # Method to return a rented book
        user = User.get_by_library_card(self.conn, library_card_number)
        if user:
            Rental.return_books(self.conn, user.user_id, isbn, quantity)
        else:
            print("User not found.")

    def list_available_books(self):
        # Method to list all available books in the library
        books = Book.list_all_available(self.conn)
        if books:
            headers = ["BookID", "Title", "Author", "Year", "Genre", "ISBN", "Count"]
            print(tabulate(books, headers=headers, tablefmt='grid'))
        else:
            print("No available books found.")

    def list_overdue_books(self):
        # Method to list all overdue books
        rentals = Rental.list_overdue(self.conn)
        if rentals:
            headers = ["RentalID", "LibraryCardNumber", "ISBN", "RentalDate", "ReturnDate", "Returned", "Quantity"]
            print(tabulate(rentals, headers=headers, tablefmt='grid'))
        else:
            print("No overdue books found.")

    def list_all_rented_books(self):
        # Method to list all currently rented books
        rentals = Rental.list_all_rented_books(self.conn)
        if rentals:
            headers = ["RentalID", "LibraryCardNumber", "ISBN", "RentalDate", "ReturnDate", "Returned", "Quantity"]
            print(tabulate(rentals, headers=headers, tablefmt='grid'))
        else:
            print("No rented books found.")

    def list_total_overdue_books(self):
        # Method to list the total number of overdue books
        total_overdue = Rental.total_overdue(self.conn)
        print(tabulate([total_overdue], headers=['TotalOverdue'], tablefmt='grid'))

    def list_rented_books(self, library_card_number):
        # Method to list all books rented by a specific user
        user = User.get_by_library_card(self.conn, library_card_number)
        if user:
            rentals = Rental.list_rented_by_user(self.conn, user.user_id)
            if rentals:
                headers = ["BookID", "Title", "Author", "Year", "Genre", "ISBN", "RentalDate", "ReturnDate", "Quantity", "Returned"]
                print(tabulate(rentals, headers=headers, tablefmt='grid'))
            else:
                print("No rented books found for this user.")
        else:
            print("User not found.")

    def search_books(self, search_term):
        # Method to search for books by title or author
        books = Book.search(self.conn, search_term)
        if books:
            headers = ["BookID", "Title", "Author", "Year", "Genre", "ISBN", "Count"]
            print(tabulate(books, headers=headers, tablefmt='grid'))
        else:
            print("No books found with the given search term.")

    def top_books_by_genre_library(self):
        # Method to list the top books in the library by genre
        top_books = Book.top_books_by_genre(self.conn)
        print(tabulate(top_books, headers=["Genre", "TotalBooks"], tablefmt='grid'))

    def top_books_by_genre_rented(self):
        # Method to list the top rented books by genre
        top_rented_books = Rental.top_books_by_genre(self.conn)
        print(tabulate(top_rented_books, headers=["Genre", "TotalRented"], tablefmt='grid'))

    def return_available_books(self, isbn):
        # Method to get the count of available books by ISBN
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT Count FROM Book WHERE ISBN = ?
        ''', (isbn,))
        book_count = cursor.fetchone()
        if book_count:
            return book_count[0]
        return 0

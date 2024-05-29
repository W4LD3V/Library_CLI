import uuid  # Import the uuid module to generate unique identifiers
from datetime import datetime, date  # Import datetime and date classes from the datetime module
from utils.utils import add_one_year  # Import the add_one_year function from the utils.utils module

class User:
    def __init__(self, fullname):
        # Constructor to initialize the User object with a full name
        self.library_card_number = str(uuid.uuid4())  # Generate a unique library card number
        self.fullname = fullname  # Set the full name of the user
        self.valid_until = add_one_year(datetime.today()).strftime('%Y-%m-%d')  # Set the validity date to one year from today

    def save(self, conn):
        # Method to save the user details into the database
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            INSERT INTO User (LibraryCardNumber, FullName, ValidUntil)
            VALUES (?, ?, ?)
        ''', (self.library_card_number, self.fullname, self.valid_until))  # Execute the SQL query to insert user details
        conn.commit()  # Commit the transaction to save changes to the database

    @staticmethod
    def authenticate(conn, library_card_number):
        # Static method to authenticate a user using their library card number
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT * FROM User WHERE LibraryCardNumber=?
        ''', (library_card_number,))  # Execute the SQL query to select a user with the matching library card number
        return cursor.fetchone()  # Fetch and return the result of the query (None if no match found)

    @staticmethod
    def get_by_library_card(conn, library_card_number):
        # Static method to get a user by their library card number
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT * FROM User WHERE LibraryCardNumber=?
        ''', (library_card_number,))  # Execute the SQL query to select a user with the matching library card number
        row = cursor.fetchone()  # Fetch the result of the query
        if row:
            user = User(row[2])  # Use the full name from the row to initialize the User object
            user.user_id = row[0]  # Set the user ID
            user.library_card_number = row[1]  # Set the library card number
            user.valid_until = row[3]  # Set the validity date
            return user  # Return the User object
        return None  # Return None if no user is found

    @staticmethod
    def check_rental_status(conn, library_card_number):
        # Static method to check if a user has any overdue rentals
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
            FROM Rental
            JOIN User ON Rental.UserID = User.UserID
            WHERE User.LibraryCardNumber = ? AND Rental.Returned = 0
            ORDER BY Rental.ReturnDate ASC
        ''', (library_card_number,))  # Execute the SQL query to select rentals for the user that are not returned
        rentals = cursor.fetchall()  # Fetch all the results of the query
        today = date.today()  # Get today's date
        
        for rental in rentals:
            rental_id, book_id, quantity, return_date = rental  # Unpack the rental details
            return_date = date.fromisoformat(return_date)  # Convert the return date to a date object
            if return_date < today:
                return True  # There is an overdue book
        
        return False  # No overdue books

    def has_overdue_books(self, conn):
        # Method to check if the user has any overdue books
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
            FROM Rental
            JOIN User ON Rental.UserID = User.UserID
            WHERE User.UserID = ? AND Rental.Returned = 0
            ORDER BY Rental.ReturnDate ASC
        ''', (self.user_id,))  # Execute the SQL query to select rentals for the user that are not returned
        rentals = cursor.fetchall()  # Fetch all the results of the query
        today = datetime.today().date()  # Get today's date as a date object
        for rental in rentals:
            rental_id, book_id, quantity, return_date = rental  # Unpack the rental details
            if datetime.strptime(return_date, '%Y-%m-%d').date() < today:
                return True  # There is an overdue book
        return False  # No overdue books

from datetime import datetime
from utils.utils import add_one_month

class Rental:
    def __init__(self, user_id, isbn, return_date, quantity):
        # Constructor to initialize the Rental object with user ID, ISBN, return date, and quantity
        self.user_id = user_id  # Set the user ID
        self.isbn = isbn  # Set the book ISBN
        self.return_date = return_date if return_date else add_one_month(datetime.today()).strftime('%Y-%m-%d')  # Set the return date, default is one month from today
        self.quantity = quantity if quantity else 1  # Set the quantity, default is 1

    def save(self, conn):
        # Method to save the rental details into the database
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT BookID, Count FROM Book WHERE ISBN = ?
        ''', (self.isbn,))  # Execute the SQL query to check if the book exists and get its count
        book = cursor.fetchone()  # Fetch the result of the query
        if book and book[1] >= self.quantity:
            # If the book exists and has enough copies, save the rental
            book_id = book[0]
            cursor.execute('''
                INSERT INTO Rental (UserID, BookID, ReturnDate, Quantity)
                VALUES (?, ?, ?, ?)
            ''', (self.user_id, book_id, self.return_date, self.quantity))  # Insert the rental details
            cursor.execute('''
                UPDATE Book SET Count = Count - ? WHERE BookID = ?
            ''', (self.quantity, book_id))  # Update the book count
            conn.commit()  # Commit the transaction to save changes to the database
        else:
            print("Not enough books available.")  # Print message if not enough books are available

    @staticmethod
    def return_books(conn, user_id, isbn, return_quantity=None):
        # Static method to return rented books
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
            FROM Rental
            JOIN User ON Rental.UserID = User.UserID
            JOIN Book ON Rental.BookID = Book.BookID
            WHERE User.UserID = ? AND Book.ISBN = ? AND Rental.Returned = 0
            ORDER BY Rental.ReturnDate ASC
        ''', (user_id, isbn))  # Execute the SQL query to get the rentals for the user and book
        rentals = cursor.fetchall()  # Fetch all the results of the query
        if not rentals:
            print("Error: No active rental found for this ISBN and user.")  # Print error message if no rentals found
            return
        if return_quantity is None:
            return_quantity = sum(rental[2] for rental in rentals)  # Calculate the total quantity to return
        remaining_quantity_to_return = return_quantity  # Set the remaining quantity to return
        for rental in rentals:
            rental_id, book_id, quantity, return_date = rental
            if remaining_quantity_to_return <= 0:
                break  # Break the loop if no remaining quantity to return
            if remaining_quantity_to_return >= quantity:
                cursor.execute('''
                    UPDATE Rental SET Returned = 1, Quantity = 0 WHERE RentalID = ?
                ''', (rental_id,))  # Update the rental as returned
                remaining_quantity_to_return -= quantity  # Decrease the remaining quantity to return
            else:
                cursor.execute('''
                    UPDATE Rental SET Quantity = Quantity - ? WHERE RentalID = ?
                ''', (remaining_quantity_to_return, rental_id))  # Update the rental quantity
                remaining_quantity_to_return = 0  # Set remaining quantity to return to 0
            cursor.execute('''
                UPDATE Book SET Count = Count + ? WHERE BookID = ?
            ''', (quantity, book_id))  # Update the book count
        conn.commit()  # Commit the transaction to save changes to the database
        if remaining_quantity_to_return > 0:
            print(f"Warning: Not all requested quantities were returned. {remaining_quantity_to_return} books could not be returned.")  # Print warning if not all quantities were returned

    @staticmethod
    def list_overdue(conn):
        # Static method to list all overdue rentals
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT 
                Rental.RentalID,
                User.LibraryCardNumber,
                Book.ISBN,
                Rental.RentalDate,
                Rental.ReturnDate,
                Rental.Returned,
                Rental.Quantity
            FROM Rental
            JOIN User ON Rental.UserID = User.UserID
            JOIN Book ON Rental.BookID = Book.BookID
            WHERE Rental.ReturnDate < ? AND Rental.Returned = 0
        ''', (datetime.today().strftime('%Y-%m-%d'),))  # Execute the SQL query to select overdue rentals
        return cursor.fetchall()  # Fetch and return all the results of the query

    @staticmethod
    def list_all_rented_books(conn):
        # Static method to list all rented books
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT 
                Rental.RentalID,
                User.LibraryCardNumber,
                Book.ISBN,
                Rental.RentalDate,
                Rental.ReturnDate,
                Rental.Returned,
                Rental.Quantity
            FROM Rental
            JOIN User ON Rental.UserID = User.UserID
            JOIN Book ON Rental.BookID = Book.BookID
            WHERE Rental.Returned = 0
        ''')  # Execute the SQL query to select all rented books
        return cursor.fetchall()  # Fetch and return all the results of the query

    @staticmethod
    def total_overdue(conn):
        # Static method to get the total quantity of overdue books
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT SUM(Quantity) as TotalOverdue
            FROM Rental
            WHERE ReturnDate < ? AND Returned = 0
        ''', (datetime.today().strftime('%Y-%m-%d'),))  # Execute the SQL query to get the total quantity of overdue books
        return cursor.fetchone()  # Fetch and return the result of the query

    @staticmethod
    def list_rented_by_user(conn, user_id):
        # Static method to list all rented books by a specific user
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT 
                Book.BookID,
                Book.Title,
                Book.Author,
                Book.Year,
                Book.Genre,
                Book.ISBN,
                Rental.RentalDate,
                Rental.ReturnDate,
                Rental.Quantity,
                Rental.Returned
            FROM 
                User
            JOIN 
                Rental ON User.UserID = Rental.UserID
            JOIN 
                Book ON Rental.BookID = Book.BookID
            WHERE 
                User.UserID = ? AND Rental.Returned = 0
        ''', (user_id,))  # Execute the SQL query to select all rented books by the user
        return cursor.fetchall()  # Fetch and return all the results of the query

    @staticmethod
    def top_books_by_genre(conn):
        # Static method to get the top rented books by genre
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT b.Genre, SUM(r.Quantity) as TotalRented
            FROM Rental r
            JOIN Book b ON r.BookID = b.BookID
            GROUP BY b.Genre
            ORDER BY TotalRented DESC
            LIMIT 5
        ''')  # Execute the SQL query to get the top rented books by genre
        return cursor.fetchall()  # Fetch and return all the results of the query

import uuid
from datetime import datetime
from utils.utils import add_one_year, add_one_month
from datetime import date, datetime

class Librarian:
    def __init__(self, username, password, fullname):
        self.username = username
        self.password = password
        self.fullname = fullname

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Librarian (Username, Password, FullName)
            VALUES (?, ?, ?)
        ''', (self.username, self.password, self.fullname))
        conn.commit()

    @staticmethod
    def authenticate(conn, username, password):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Librarian WHERE Username=? AND Password=?
        ''', (username, password))
        return cursor.fetchone()

class User:
    def __init__(self, fullname):
        self.library_card_number = str(uuid.uuid4())
        self.fullname = fullname
        self.valid_until = add_one_year(datetime.today()).strftime('%Y-%m-%d')

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO User (LibraryCardNumber, FullName, ValidUntil)
            VALUES (?, ?, ?)
        ''', (self.library_card_number, self.fullname, self.valid_until))
        conn.commit()

    @staticmethod
    def authenticate(conn, library_card_number):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM User WHERE LibraryCardNumber=?
        ''', (library_card_number,))
        return cursor.fetchone()

    @staticmethod
    def get_by_library_card(conn, library_card_number):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM User WHERE LibraryCardNumber=?
        ''', (library_card_number,))
        row = cursor.fetchone()
        if row:
            user = User(row[2])  # Use the FullName to initialize
            user.user_id = row[0]
            user.library_card_number = row[1]
            user.valid_until = row[3]
            return user
        return None
    
    @staticmethod
    def check_rental_status(conn, library_card_number):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
            FROM Rental
            JOIN User ON Rental.UserID = User.UserID
            WHERE User.LibraryCardNumber = ? AND Rental.Returned = 0
            ORDER BY Rental.ReturnDate ASC
        ''', (library_card_number,))
        
        rentals = cursor.fetchall()
        today = date.today()
        
        for rental in rentals:
            rental_id, book_id, quantity, return_date = rental
            return_date = date.fromisoformat(return_date)
            if return_date < today:
                return True  # There is an overdue book
        
        return False  # No overdue books

    def has_overdue_books(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
            FROM Rental
            JOIN User ON Rental.UserID = User.UserID
            WHERE User.UserID = ? AND Rental.Returned = 0
            ORDER BY Rental.ReturnDate ASC
        ''', (self.user_id,))
        rentals = cursor.fetchall()
        today = datetime.today().date()
        for rental in rentals:
            rental_id, book_id, quantity, return_date = rental
            if datetime.strptime(return_date, '%Y-%m-%d').date() < today:
                return True
        return False

class Book:
    def __init__(self, title, author, year, genre, isbn, count):
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.isbn = isbn
        self.count = count

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT BookID, Count FROM Book WHERE ISBN = ?
        ''', (self.isbn,))
        book = cursor.fetchone()
        if book:
            book_id, current_count = book
            new_count = current_count + self.count
            cursor.execute('''
                UPDATE Book SET Count = ? WHERE BookID = ?
            ''', (new_count, book_id))
        else:
            cursor.execute('''
                INSERT INTO Book (Title, Author, Year, Genre, ISBN, Count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.title, self.author, self.year, self.genre, self.isbn, self.count))
        conn.commit()

    @staticmethod
    def delete_by_isbn(conn, isbn, count_to_delete=None):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(Count) FROM Book WHERE ISBN=?
        ''', (isbn,))
        total_books = cursor.fetchone()[0]
        if count_to_delete is None or count_to_delete >= total_books:
            cursor.execute('''
                DELETE FROM Book WHERE ISBN=?
            ''', (isbn,))
        else:
            books_to_delete = count_to_delete
            while books_to_delete > 0:
                cursor.execute('''
                    SELECT BookID, Count FROM Book WHERE ISBN=? LIMIT 1
                ''', (isbn,))
                book = cursor.fetchone()
                if book is None:
                    break
                book_id, book_count = book
                if book_count > books_to_delete:
                    cursor.execute('''
                        UPDATE Book SET Count = Count - ? WHERE BookID = ?
                    ''', (books_to_delete, book_id))
                    books_to_delete = 0
                else:
                    cursor.execute('''
                        DELETE FROM Book WHERE BookID = ?
                    ''', (book_id,))
                    books_to_delete -= book_count
        conn.commit()

    def delete_book_by_year(self, year):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM Book WHERE Year <= ?
        ''', (year,))
        self.conn.commit()

    @staticmethod
    def delete_by_year(conn, year):
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM Book WHERE Year <= ?
        ''', (year,))
        conn.commit()

    @staticmethod
    def list_all_available(conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT BookID, Title, Author, Year, Genre, ISBN, Count FROM Book WHERE Count > 0
        ''')
        return cursor.fetchall()

    @staticmethod
    def search(conn, search_term):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Book
            WHERE Title LIKE '%' || ? || '%'
               OR Author LIKE '%' || ? || '%'
        ''', (search_term, search_term))
        return cursor.fetchall()

    @staticmethod
    def top_books_by_genre(conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Genre, SUM(Count) as TotalBooks
            FROM Book
            GROUP BY Genre
            ORDER BY TotalBooks DESC
            LIMIT 5
        ''')
        return cursor.fetchall()

class Rental:
    def __init__(self, user_id, isbn, return_date, quantity):
        self.user_id = user_id
        self.isbn = isbn
        self.return_date = return_date if return_date else add_one_month(datetime.today()).strftime('%Y-%m-%d')
        self.quantity = quantity if quantity else 1

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT BookID, Count FROM Book WHERE ISBN = ?
        ''', (self.isbn,))
        book = cursor.fetchone()
        if book and book[1] >= self.quantity:
            book_id = book[0]
            cursor.execute('''
                INSERT INTO Rental (UserID, BookID, ReturnDate, Quantity)
                VALUES (?, ?, ?, ?)
            ''', (self.user_id, book_id, self.return_date, self.quantity))
            cursor.execute('''
                UPDATE Book SET Count = Count - ? WHERE BookID = ?
            ''', (self.quantity, book_id))
            conn.commit()
        else:
            print("Not enough books available.")

    @staticmethod
    def return_books(conn, user_id, isbn, return_quantity=None):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Rental.RentalID, Rental.BookID, Rental.Quantity, Rental.ReturnDate
            FROM Rental
            JOIN User ON Rental.UserID = User.UserID
            JOIN Book ON Rental.BookID = Book.BookID
            WHERE User.UserID = ? AND Book.ISBN = ? AND Rental.Returned = 0
            ORDER BY Rental.ReturnDate ASC
        ''', (user_id, isbn))
        rentals = cursor.fetchall()
        if not rentals:
            print("Error: No active rental found for this ISBN and user.")
            return
        if return_quantity is None:
            return_quantity = sum(rental[2] for rental in rentals)
        remaining_quantity_to_return = return_quantity
        for rental in rentals:
            rental_id, book_id, quantity, return_date = rental
            if remaining_quantity_to_return <= 0:
                break
            if remaining_quantity_to_return >= quantity:
                cursor.execute('''
                    UPDATE Rental SET Returned = 1, Quantity = 0 WHERE RentalID = ?
                ''', (rental_id,))
                remaining_quantity_to_return -= quantity
            else:
                cursor.execute('''
                    UPDATE Rental SET Quantity = Quantity - ? WHERE RentalID = ?
                ''', (remaining_quantity_to_return, rental_id))
                remaining_quantity_to_return = 0
            cursor.execute('''
                UPDATE Book SET Count = Count + ? WHERE BookID = ?
            ''', (quantity, book_id))
        conn.commit()
        if remaining_quantity_to_return > 0:
            print(f"Warning: Not all requested quantities were returned. {remaining_quantity_to_return} books could not be returned.")

    @staticmethod
    def list_overdue(conn):
        cursor = conn.cursor()
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
        ''', (datetime.today().strftime('%Y-%m-%d'),))
        return cursor.fetchall()

    @staticmethod
    def list_all_rented_books(conn):
        cursor = conn.cursor()
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
        ''')
        return cursor.fetchall()

    @staticmethod
    def total_overdue(conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(Quantity) as TotalOverdue
            FROM Rental
            WHERE ReturnDate < ? AND Returned = 0
        ''', (datetime.today().strftime('%Y-%m-%d'),))
        return cursor.fetchone()

    @staticmethod
    def list_rented_by_user(conn, user_id):
        cursor = conn.cursor()
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
        ''', (user_id,))
        return cursor.fetchall()


    @staticmethod
    def top_books_by_genre(conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.Genre, SUM(r.Quantity) as TotalRented
            FROM Rental r
            JOIN Book b ON r.BookID = b.BookID
            GROUP BY b.Genre
            ORDER BY TotalRented DESC
            LIMIT 5
        ''')
        return cursor.fetchall()

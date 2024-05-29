class Book:
    def __init__(self, title, author, year, genre, isbn, count):
        # Constructor to initialize the Book object with title, author, year, genre, ISBN, and count
        self.title = title  # Set the book title
        self.author = author  # Set the book author
        self.year = year  # Set the publication year
        self.genre = genre  # Set the book genre
        self.isbn = isbn  # Set the book ISBN
        self.count = count  # Set the number of copies available

    def save(self, conn):
        # Method to save the book details into the database
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT BookID, Count FROM Book WHERE ISBN = ?
        ''', (self.isbn,))  # Execute the SQL query to check if the book already exists in the database
        book = cursor.fetchone()  # Fetch the result of the query
        if book:
            # If the book exists, update the count of copies
            book_id, current_count = book
            new_count = current_count + self.count  # Calculate the new count of copies
            cursor.execute('''
                UPDATE Book SET Count = ? WHERE BookID = ?
            ''', (new_count, book_id))  # Execute the SQL query to update the book count
        else:
            # If the book does not exist, insert it into the database
            cursor.execute('''
                INSERT INTO Book (Title, Author, Year, Genre, ISBN, Count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.title, self.author, self.year, self.genre, self.isbn, self.count))  # Execute the SQL query to insert the book details
        conn.commit()  # Commit the transaction to save changes to the database

    @staticmethod
    def delete_by_isbn(conn, isbn, count_to_delete=None):
        # Static method to delete a book by its ISBN
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT SUM(Count) FROM Book WHERE ISBN=?
        ''', (isbn,))  # Execute the SQL query to get the total count of books with the given ISBN
        total_books = cursor.fetchone()[0]  # Fetch the total count of books
        if count_to_delete is None or count_to_delete >= total_books:
            # If count_to_delete is None or greater than or equal to total_books, delete all books with the given ISBN
            cursor.execute('''
                DELETE FROM Book WHERE ISBN=?
            ''', (isbn,))  # Execute the SQL query to delete the books
        else:
            # If count_to_delete is less than total_books, delete the specified count of books
            books_to_delete = count_to_delete
            while books_to_delete > 0:
                cursor.execute('''
                    SELECT BookID, Count FROM Book WHERE ISBN=? LIMIT 1
                ''', (isbn,))  # Execute the SQL query to get a single book record with the given ISBN
                book = cursor.fetchone()  # Fetch the book record
                if book is None:
                    break  # Break the loop if no book is found
                book_id, book_count = book
                if book_count > books_to_delete:
                    # If the book count is greater than books_to_delete, update the count
                    cursor.execute('''
                        UPDATE Book SET Count = Count - ? WHERE BookID = ?
                    ''', (books_to_delete, book_id))  # Execute the SQL query to update the book count
                    books_to_delete = 0  # Set books_to_delete to 0
                else:
                    # If the book count is less than or equal to books_to_delete, delete the book record
                    cursor.execute('''
                        DELETE FROM Book WHERE BookID = ?
                    ''', (book_id,))  # Execute the SQL query to delete the book
                    books_to_delete -= book_count  # Decrease books_to_delete by the book count
        conn.commit()  # Commit the transaction to save changes to the database

    def delete_book_by_year(self, year):
        # Method to delete books published on or before a given year
        cursor = self.conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            DELETE FROM Book WHERE Year <= ?
        ''', (year,))  # Execute the SQL query to delete the books
        self.conn.commit()  # Commit the transaction to save changes to the database

    @staticmethod
    def delete_by_year(conn, year):
        # Static method to delete books published on or before a given year
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            DELETE FROM Book WHERE Year <= ?
        ''', (year,))  # Execute the SQL query to delete the books
        conn.commit()  # Commit the transaction to save changes to the database

    @staticmethod
    def list_all_available(conn):
        # Static method to list all available books
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT BookID, Title, Author, Year, Genre, ISBN, Count FROM Book WHERE Count > 0
        ''')  # Execute the SQL query to select all available books
        return cursor.fetchall()  # Fetch and return all the results of the query

    @staticmethod
    def search(conn, search_term):
        # Static method to search for books by title or author
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT * FROM Book
            WHERE Title LIKE '%' || ? || '%'
               OR Author LIKE '%' || ? || '%'
        ''', (search_term, search_term))  # Execute the SQL query to search for books by title or author
        return cursor.fetchall()  # Fetch and return all the results of the query

    @staticmethod
    def top_books_by_genre(conn):
        # Static method to get the top books by genre
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('''
            SELECT Genre, SUM(Count) as TotalBooks
            FROM Book
            GROUP BY Genre
            ORDER BY TotalBooks DESC
            LIMIT 5
        ''')  # Execute the SQL query to get the top books by genre
        return cursor.fetchall()  # Fetch and return all the results of the query

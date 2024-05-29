from getpass import getpass # Importuojam 'getpass' modulį, kad naudotojas galėtų įvesti slaptažodį, jo nematant.

from library import Library  # Importuojam Library modulį iš library modulio (./library.py).
from utils.utils import add_one_month  # Importuojam pagalbinį metodą iš utils modulio (../utils/.utils.py)
from datetime import date, datetime  # Importuojam date ir datetime klases iš datetime modulio

def main():
    # Kintamajam priskiriam Library klasę.
    library = Library()
    # Paleidžiam funkciją kuri įrašo pagalbinius/pradinius duomenis.
    library.insert_sample_data()

    while True:
        # Pagrindinis meniu
        print("\nWelcome to the Library Management System\n")
        print("1. Login as Admin")
        print("2. Login as User")
        print("3. Register as User")
        print("4. See top charts")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            # Admin prisijungimo procesas
            username = input("Enter username: ")
            password = getpass("Enter password: ")  # Saugus metodas įvesti slaptažodį
            admin = library.authenticate_admin(username, password)
            if admin:
                while True:
                    # Admin meniu
                    print("\nAdmin Menu\n")
                    print("1. Add Book")
                    print("2. Delete Book")
                    print("3. List Available Books")
                    print("4. List Overdue Books")
                    print("5. Logout")
                    admin_choice = input("Enter your choice: ")

                    if admin_choice == '1':
                        # Pasirinkimas pridėti naują knygą į biblioteką
                        title = input("Enter book title: ")
                        author = input("Enter author: ")

                        # Užsitikrinam, kad metai kuriuos įveda administratorius yra 'int' tipo. Taipogi paliekam pasirinkimą įvesti tuščius metus
                        while True:
                            year = input("Enter year: ")
                            try:
                                year = int(year) if year else None
                                break
                            except ValueError:
                                print("Invalid year. Please enter a valid number.")
                        
                        genre = input("Enter genre: ")

                        # Knygos identifikacinio kodo - ISBN numerio įvestis, užtikrinam, kad šis laukelis nebūtų tuščias.
                        while True:
                            isbn = input("Enter ISBN: ")
                            if isbn.strip():
                                break
                            print("ISBN cannot be empty. Please enter a valid ISBN.")
                        
                        # Knygų skaičiaus įvestis, užtikrinam, kad jis būtų 'int' tipo, 
                        # ir jeigu administratorius šį laukelį palieka tuščiu, automatiškai pridedam tik vieną knygą.
                        while True:
                            count = input("Enter count (default is 1): ")
                            try:
                                count = int(count) if count else 1
                                break
                            except ValueError:
                                print("Invalid count. Please enter a valid number.")
                        
                        # Iškviečiama funkcija pridėti knygą
                        library.add_book(title, author, year, genre, isbn, count)

                    elif admin_choice == '2':
                        # Pasirinkimas ištrinti knygą iš bibliotekos.
                        print("\nDelete Menu\n")
                        while True:
                            print("1. Remove book by ISBN")
                            print("2. Remove all books by year")
                            print("3. Go back")
                            delete_choice = input("Enter your choice: ")
                            if delete_choice == '1':
                                # Knyga ištrinama pagal specifinį ISBN kodą.
                                while True:
                                    book_isbn = input("Enter book ISBN to remove (type 'exit' to quit): ")
                                    if book_isbn.lower() == 'exit':
                                        break
                                    if book_isbn.strip() == "":
                                        print("ISBN cannot be empty. Please enter a valid ISBN.")
                                    else:
                                        break
                                if book_isbn.lower() == 'exit':
                                    break
                                # Pasirenkamas ištrinamų skaičių kiekis, užtikrinama, kad skaičius būtinai būtų 'int' tipo. 
                                # Jeigu įvestis paliekama tuščia, ištrinamos visos knygos pagal ISBN numerį.
                                while True:
                                    book_count_input = input("Enter how many books you want to delete, leave input empty if you want to delete all: ")
                                    try:
                                        book_count_to_delete = int(book_count_input) if book_count_input else None
                                        break
                                    except ValueError:
                                        print("Invalid count. Please enter a valid number.")
                                library.delete_book_by_isbn(book_isbn, book_count_to_delete)
                                print("Book/s deleted successfully.")
                                break

                            elif delete_choice == '2':
                                # Pasirinkimas ištrinti visas knygas kurios yra lygios arba senesnių metų negu, kad įvedė administratorius.
                                while True:
                                    year_input = input("Enter year of books to delete (type 'exit' to quit): ")
                                    if year_input.lower() == 'exit':
                                        break
                                    if year_input.strip() == "":
                                        print("Year cannot be empty. Please enter a valid year.")
                                    else:
                                        try:
                                            year = int(year_input)
                                            library.delete_book_by_year(year)
                                            print("Book/s deleted successfully.")
                                            break
                                        except ValueError:
                                            print("Invalid year. Please enter a valid year.")
                                if year_input.lower() == 'exit':
                                    break

                            elif delete_choice == '3':
                                break
                            else:
                                print("Invalid choice. Please try again.")
                    
                    elif admin_choice == '3':
                        # Pasirinkus kviečiama funkcija kuri parodo visas knygas bibliotekoje, kurios dar nėra išnuomuotos.
                        library.list_available_books()
                    
                    elif admin_choice == '4':
                        # Pasirinkus iškviečiamos funkcijos kurios parodo:
                        # 1. bendrą visų šiuo metu išnuomuotų knygų kiekį;
                        # 2. sąrašą knygų kur sužymėtos visios šiuo metu vėluojamos grąžinti knygos ir nuomuotojų kortelės kodai;
                        # 3. sąrašą knygų kur sužymėtos visios šiuo metu išuomotos knygos ir nuomuotojų kortelės kodai.
                        print("\n")
                        print("Total number of overdue books:")
                        library.list_total_overdue_books()
                        print("\n")
                        print("All books that are overdue:")
                        library.list_overdue_books()
                        print("\n")
                        print("All books that are rented:")
                        library.list_all_rented_books()
                        print("\n")
                    
                    elif admin_choice == '5':
                        break  # Paspaudus atsijungama nuo administatoriaus rolių.
            else:
                print("Invalid credentials")

        elif choice == '2':
            # Naudotojo korteles validavimas
            library_card_number = input("Enter your library card number: ")
            user = library.authenticate_user(library_card_number)
            if user:
                while True:
                    # Naudotojo meniu
                    print("\nUser Menu\n")
                    print("1. Rent Book")
                    print("2. Return Book")
                    print("3. List Available Books")
                    print("4. List Rented Books")
                    print("5. Search books")
                    print("6. Logout")
                    user_choice = input("Enter your choice: ")

                    if user_choice == '1':
                        # Knygos nuomavimo funkcionalumas
                        overdue = library.check_rental_status(library_card_number)
                        if overdue:
                            print("You can't rent a new book before you return all overdue books.")
                        else:
                            while True:
                                book_isbn_to_rent = input("Enter book ISBN to rent (type 'exit' to quit): ")
                                if book_isbn_to_rent.lower() == 'exit':
                                    break

                                available_books = library.return_available_books(book_isbn_to_rent)
                                if available_books == 0:
                                    print("The book doesn't exist in the library, please try a different ISBN number (type 'exit' to quit)")
                                    continue

                                while True:
                                    return_date = input("Enter return date (YYYY-MM-DD, default is 1 month): ")
                                    if not return_date:
                                        return_date = add_one_month(datetime.today()).strftime('%Y-%m-%d')

                                    try:
                                        return_formatted_date = date.fromisoformat(return_date)
                                        today = date.today()
                                        if return_formatted_date < today:
                                            print(f"Return date cannot be less than today: {today}")
                                        else:
                                            break
                                    except ValueError:
                                        print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")

                                while True:
                                    quantity_input = input(f"Enter quantity of books to rent, currently there are {available_books} book(s) in the library, (default is 1, limit is <= 3, type 'exit' to quit): ")
                                    if quantity_input.lower() == 'exit':
                                        break
                                    try:
                                        quantity = int(quantity_input) if quantity_input else 1
                                        if quantity > 3:
                                            print("Cannot rent more than 3 of the same book")
                                        elif quantity > available_books:
                                            print(f"Cannot rent more books than are available in the library ({available_books})")
                                        else:
                                            library.rent_book(library_card_number, book_isbn_to_rent, return_date, quantity)
                                            break
                                    except ValueError:
                                        print("Invalid quantity. Please enter a valid number.")
                                break  # Išėjimas iš knygos nuomos meniu

                    elif user_choice == '2':
                        # Knygos grąžinimo meniu
                        isbn = input("Enter book ISBN to return: ")
                        while True:
                            quantity = input("Enter quantity to return (leave empty to return all): ")
                            try:
                                quantity = int(quantity) if quantity else None
                                break
                            except ValueError:
                                print("Invalid quantity. Please enter a valid number.")
                        library.return_book(library_card_number, isbn, quantity)

                    elif user_choice == '3':
                        # Parodomos visos bibliotekoje esančios knygos
                        library.list_available_books()
                    
                    elif user_choice == '4':
                        # Sąrašas knygų kurias yra išsinuomaves naudotojas
                        library.list_rented_books(library_card_number)
                    
                    elif user_choice == '5':
                        # Knygų paieškos meniu
                        search_term = input("Enter search term: ")
                        library.search_books(search_term)
                    
                    elif user_choice == '6':
                        break  # Atsijungimas nuo naudotojo rolių.
            else:
                print("Invalid library card number")

        elif choice == '3':
            # Naujo naudotojo registracija
            full_name = input("Enter your full name: ")
            card_number = library.register_user(full_name)
            print(f"Registration successful. Your card number is {card_number}")

        elif choice == '4':
            # Top knygų meniu
            print("\nTop Charts Menu\n")
            while True:
                print("1. Top Library Books ranked by Genre")
                print("2. Top Rented Books ranked by Genre")
                print("3. Go back")
                chart_choice = input("Enter your choice: ")
                if chart_choice == '1':
                    library.top_books_by_genre_library()
                elif chart_choice == '2':
                    library.top_books_by_genre_rented()
                elif chart_choice == '3':
                    break
                else:
                    print("Invalid choice")
        
        elif choice == '5':
            break  # Išėjimas iš programos
        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()

from pathlib import Path
from typing import List

from Exceptions.BookExistsException import BookExistsException
from Observers.LibrarianNotificationObserver import LibrarianNotificationObserver
from Observers.LibraryNotificationSubject import LibraryNotificationSubject
from Services.ManageCsv import ManageCsv
from Models.Book import Book
from Decorator.Decorator import log_operation
from Services.Logger import Logger
from Exceptions.NegativeCopiesException import NegativeCopiesException
from Exceptions.NoCopyAvailableException import NoCopyAvailableException
from Exceptions.NonIntegerException import NonIntegerException
from Exceptions.ReturnBookNeverLoand import ReturnBookNeverLoand
from Exceptions.BookNotExistsException import BookNotExistsException



class Library:
    def __init__(self, file_path: str):
        self.books = ManageCsv(file_path)
        base_dir = Path(__file__).resolve().parent.parent

        # הגדרת נתיבים דינמיים עבור available_books ו-loaned_books
        self.avialable_books = ManageCsv(base_dir / "Files/available_books.csv")
        self.loaned_books = ManageCsv(base_dir / "Files/loaned_books.csv")
        self.waiting_list = ManageCsv.load_waiting_list_from_csv()
        log_file_path = Logger.get_dynamic_path("Files/Log")
        self.logger = Logger(log_file_path).get_logger()
        self.notification_subject = LibraryNotificationSubject()
        self.notification_observer = LibrarianNotificationObserver(self.logger)
        self.notification_subject.attach(self.notification_observer)

    @log_operation("book borrowed")
    def lend_book(self, title: str):
        books = self.books.read_all()
        # חיפוש הספר ברשימת הספרים בקובץ לפי הכותרת
        book_index = books.index[books['title'].str.lower() == title.lower()]

        if not book_index.empty:
            book_row = books.loc[book_index[0]]

            # המרה לאובייקט Book
            book = Book(
                title=book_row['title'],
                author=book_row['author'],
                year=int(book_row['year']),
                genre=book_row['genre'],
                copies=int(book_row['copies']),
                available_copies=int(book_row['available_copies']),
                is_loaned=book_row['is_loaned']
            )

            # בדיקה אם יש עותקים זמינים
            if book.available_copies > 0:
                book.available_copies -= 1
                books.at[book_index[0], 'available_copies'] -= 1
                if book.available_copies == 0:
                    book.is_loaned = "Yes"
                    books.at[book_index[0], 'is_loaned'] = "Yes"

                # עדכון רשימות וקבצים
                self.avialable_books.delete_row(book)  # כאן מועבר אובייקט Book
                self.loaned_books.add_row(book)
                self.avialable_books.save_csv()
                self.loaned_books.save_csv()
                self.books.save_csv()
            else:
                raise NoCopyAvailableException(f"No available copies for '{title}'.")
        else:
            raise BookNotExistsException(f"Book '{title}' not found in the library.")
    @log_operation("book returned")
    def return_book(self, book: Book):
        """
        החזרת ספר: מעדכנת את העותקים הזמינים ובודקת אם יש רשימת המתנה.
        :param book: אובייקט מסוג Book להחזרה.
        """
        books = self.books.read_all()

        # חיפוש הספר ברשימת הספרים בקובץ
        book_index = books.index[(books['title'] == book.title) & (books['author'] == book.author)]

        if not book_index.empty:
            # עדכון מספר העותקים הזמינים
            book_row = books.loc[book_index[0]]
            if book.available_copies == 0:
              book.available_copies += 1
              books.at[book_index[0], 'available_copies'] += 1
              book.is_loaned="No"
              books.at[book_index[0], 'is_loaned'] = "No"
              newBook=self.books.get_book_by_title(book.title,book.author)
              self.loaned_books.delete_row(newBook)
              self.avialable_books.add_row(newBook)
            else:
                if book.available_copies > 0 and book.available_copies < book.copies:
                  book.available_copies += 1
                  books.at[book_index[0], 'available_copies'] += 1
                else:
                     if(book.available_copies == book.copies):
                         raise ReturnBookNeverLoand()
            title_lower = book.title.lower()
            if title_lower in self.waiting_list and self.waiting_list[title_lower]:
                next_customer = self.waiting_list[title_lower].pop(0)
                self.save_waitinglist()
                self.notification_subject.notify(book, [next_customer], "return")
                self.lend_book(title_lower)
            self.books.save_csv()
            self.loaned_books.save_csv()
            self.avialable_books.save_csv()
        else:
            raise BookNotExistsException()






    @log_operation("book added")
    def add_book(self, book: Book):
        """
        הוספת ספר חדש לספרייה ולשורות הקובץ.
        :param book: אובייקט של ספר.
        """
        try:
            # בדיקה אם הספר כבר קיים בספרייה
            books = self.books.read_all()
            existing_book = books[
                (books["title"].str.lower() == book.title.lower()) &
                (books["author"].str.lower() == book.author.lower())
                ]
            if not existing_book.empty:
                raise BookExistsException(f"Book '{book.title}' by {book.author} already exists in the library.")

            # המרת year ו-copies ל-int
            book.year = int(book.year)
            book.copies = int(book.copies)

            # בדיקה אם הערכים חיוביים
            if book.copies <= 0:
                raise NegativeCopiesException("Total copies must be a positive integer.")
        except ValueError:
            # אם לא ניתן להמיר ל-int
            raise NonIntegerException("Year and total copies must be integers.")

        # הוספת הספר לרשימות המתאימות
        self.books.add_row(book)
        if book.is_loaned == "No":
            self.avialable_books.add_row(book)
            self.avialable_books.save_csv()
        elif book.is_loaned == "Yes":
            self.loaned_books.add_row(book)
            self.loaned_books.save_csv()

    def display_waitlist(self, book_title: str):
        """
        מציגת רשימת המתנה לספר מסוים.
        :param book_title: שם הספר.
        """
        if book_title in self.waitlist:
            waitlist = self.waitlist[book_title]
            if waitlist:
                print(f"Waitlist for '{book_title}':")
                for user in waitlist:
                    print(f"- {user['name']} (Email: {user['email']}, ID: {user['id']})")
            else:
                print(f"No waitlist for '{book_title}'.")
        else:
            print(f"Book '{book_title}' has no waitlist.")


    @log_operation("book removed")
    def delete_book(self, title, author):
        """
        מחיקת ספר על פי שם הספר ושם המחבר.
        """
        try:
            # חיפוש הספר
            matching_books = [
                book for book in self.books.read_all_as_objects("title").values()
                if book.title.lower() == title.lower() and book.author.lower() == author.lower()
            ]

            if not matching_books:
                # השלכת חריגה אם הספר לא נמצא
                raise ValueError()

            # מחיקת הספר
            book_to_delete = matching_books[0]
            self.books.delete_row(book_to_delete)
            if book_to_delete.is_loaned == "Yes":
                self.loaned_books.delete_row(book_to_delete)
                self.loaned_books.save_csv()
            if book_to_delete.is_loaned == "No":
                self.avialable_books.delete_row(book_to_delete)
                self.avialable_books.save_csv()


        except ValueError as ve:
            # טיפול במקרה שהספר לא נמצא
            raise ve

        except Exception as e:
            # טיפול בשגיאות כלליות
            raise e

    def get_waiting_list(self):
        return self.waiting_list


    @log_operation("add to waiting list")
    def waiting_for_book(self, title, customer):
        if title.lower() in self.waiting_list:
            for existing_customer in self.waiting_list[title.lower()]:
                if existing_customer.name == customer.name and existing_customer.phone == customer.phone:
                    raise ValueError(f"Customer {customer.name} is already in waiting list for book '{title}'")
        else:
            self.waiting_list[title.lower()] = []

        self.waiting_list[title.lower()].append(customer)
        self.save_waitinglist()

    def save_waitinglist(self):
            """שומר את רשימת ההמתנה."""
            ManageCsv.save_waiting_list_to_csv(self.waiting_list)

    @log_operation("displayed")
    def get_popular_books(self, limit=10):
        """
        מחזירה את 10 הספרים הפופולריים ביותר על פי:
        1. מספר העותקים המושאלים
        2. גודל רשימת ההמתנה

        Args:
            limit (int): מספר הספרים להחזרה (ברירת מחדל: 10)

        Returns:
            List[Tuple[str, int, int, int]]: רשימה של טאפלים (שם הספר, ציון ביקוש כולל, עותקים מושאלים, אנשים בהמתנה)
        """
        book_demand = []

        books_data = self.books.read_all()
        for _, row in books_data.iterrows():
            # שם הספר
            title = row['title']

            # מספר העותקים הכולל ומושאלים
            total_copies = int(row['copies'])
            available_copies = int(row['available_copies'])
            borrowed_copies = total_copies - available_copies

            # מספר האנשים ברשימת ההמתנה לספר
            waiting_list_count = len(self.waiting_list.get(title.lower(), []))

            # חישוב ציון הביקוש הכולל
            total_demand = borrowed_copies + waiting_list_count

            book_demand.append((
                title,  # שם הספר
                total_demand,  # ציון ביקוש כולל
                borrowed_copies,  # עותקים מושאלים
                waiting_list_count  # אנשים ברשימת ההמתנה
            ))

        # מיון הספרים לפי ציון הביקוש בסדר יורד
        sorted_books = sorted(book_demand, key=lambda x: x[1], reverse=True)

        # החזרת הכמות המבוקשת של ספרים
        return sorted_books[:limit]





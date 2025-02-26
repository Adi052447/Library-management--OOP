import os
import pandas as pd
import pytest
from Services.Library import Library
from Models.Book import Book
from Models.Customer import Customer
from Exceptions.NegativeCopiesException import NegativeCopiesException
from Exceptions.NoCopyAvailableException import NoCopyAvailableException
from Exceptions.NonIntegerException import NonIntegerException
from Exceptions.BookNotExistsException import BookNotExistsException
from Exceptions.ReturnBookNeverLoand import ReturnBookNeverLoand


def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), f"../Files/{filename}")

# פונקציה לקריאת המצב ההתחלתי של קובץ CSV
def backup_csv(file_path):
    file_path = get_file_path(file_path)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()


# פונקציה להחזרת הקובץ למצבו המקורי
def restore_csv(file_path, original_data):
    file_path = get_file_path(file_path)
    original_data.to_csv(file_path, index=False)


@pytest.fixture(scope="session", autouse=True)
def manage_library_files():
    # גיבוי המצב ההתחלתי של כל הקבצים
    library_backup = backup_csv("books.csv")
    available_backup = backup_csv("available_books.csv")
    loaned_backup = backup_csv("loaned_books.csv")
    waitlisted_backup = backup_csv("waiting_list.csv")

    yield  # הרצת הטסטים

    # החזרת הקבצים למצב ההתחלתי
    restore_csv("books.csv", library_backup)
    restore_csv("available_books.csv", available_backup)
    restore_csv("loaned_books.csv", loaned_backup)
    restore_csv("waiting_list.csv", waitlisted_backup)


# שאר הטסטים נשארים ללא שינוי
def setup_library():
    library = Library(get_file_path("books.csv"))
    return library


@pytest.fixture
def library():
    return setup_library()


# כל הטסטים כמו בקוד המקורי

def test_add_book_valid(library):
    # בדיקה של הוספת ספר תקינה
    book = Book(title="Test Book", author="Test Author", year=2021, genre="Fiction", copies=5, available_copies=5, is_loaned="No")
    library.add_book(book)
    assert book.title in library.books.read_all()["title"].values


def test_add_book_negative_copies(library):
    # בדיקה של הוספת ספר עם מספר עותקים שלילי
    book = Book(title="Invalid Book", author="Test Author", year=2021, genre="Fiction", copies=-3, available_copies=0, is_loaned="No")
    with pytest.raises(NegativeCopiesException):
        library.add_book(book)

def test_add_book_non_integer_year(library):
    # בדיקה של הוספת ספר עם שנה שאינה מספר שלם
    book = Book(title="Invalid Book", author="Test Author", year="YearString", genre="Fiction", copies=3, available_copies=3, is_loaned="No")
    with pytest.raises(NonIntegerException):
        library.add_book(book)


def test_lend_book_success(library):
    # בדיקה של השאלת ספר בהצלחה
    book_title = "Test Books"
    book = Book(title=book_title, author="Test Author", year=2021, genre="Fiction", copies=5, available_copies=1, is_loaned="No")
    library.add_book(book)
    library.lend_book(book_title)
    assert book_title in library.loaned_books.read_all()["title"].values
    assert library.books.read_all().loc[library.books.read_all()["title"] == book_title, "available_copies"].iloc[0] == 0

def test_lend_book_no_copies(library):
    # בדיקה של השאלת ספר ללא עותקים זמינים
    book_title = "Unavailable Book"
    book = Book(title=book_title, author="Author Test", year=2020, genre="Non-fiction", copies=1, available_copies=0, is_loaned="Yes")
    library.add_book(book)
    with pytest.raises(NoCopyAvailableException):
        library.lend_book(book_title)


def test_lend_book_not_exists(library):
    # בדיקה של השאלת ספר שלא קיים בספרייה
    with pytest.raises(BookNotExistsException):
        library.lend_book("Nonexistent Book")


def test_return_book_success(library):
    # בדיקה של החזרת ספר בהצלחה
    book_title = "Returned Book"
    book = Book(title=book_title, author="Author Test", year=2020, genre="Non-fiction", copies=1, available_copies=0, is_loaned="Yes")
    library.add_book(book)
    library.return_book(book)
    assert book_title in library.avialable_books.read_all()["title"].values
    assert library.books.read_all().loc[library.books.read_all()["title"] == book_title, "available_copies"].iloc[0] == 1


def test_return_book_not_loaned(library):
    # בדיקה של החזרת ספר שלא הושאל מעולם
    book_title = "Never Loaned"
    book = Book(title=book_title, author="Author Test", year=2020, genre="Non-fiction", copies=1, available_copies=1, is_loaned="No")
    library.add_book(book)
    with pytest.raises(ReturnBookNeverLoand):
        library.return_book(book)


def test_delete_book_success(library):
    # בדיקה של מחיקת ספר בהצלחה
    book_title = "Book to Delete"
    book = Book(title=book_title, author="Author Test", year=2020, genre="fiction", copies=1, available_copies=1, is_loaned="No")
    library.add_book(book)
    library.delete_book(book_title, "Author Test")
    assert book_title not in library.books.read_all()["title"].values

def test_waiting_list(library):
    # בדיקה של הוספת לקוח לרשימת המתנה לספר
    book_title = "Book with Waiting List"
    book = Book(title=book_title, author="Author Test", year=2020, genre="Non-fiction", copies=1, available_copies=0, is_loaned="Yes")
    customer = Customer(name="Test Customer", phone="0521111111")
    library.add_book(book)
    library.waiting_for_book(book_title, customer)
    assert customer in library.waiting_list[book_title.lower()]

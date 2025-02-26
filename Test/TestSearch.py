import logging

import pytest
from Models.Book import Book
from search.SearchStrategy import TitleSearchStrategy, AuthorSearchStrategy, GenreSearchStrategy, YearSearchStrategy

logging.disable(logging.CRITICAL)


@pytest.fixture
def sample_books():
    return {
        1: Book(title="Python Programming", author="John Smith", year=2020, genre="Education", copies=10, available_copies=5, is_loaned="No"),
        2: Book(title="Learning Java", author="Jane Doe", year=2019, genre="Education", copies=8, available_copies=2, is_loaned="Yes"),
        3: Book(title="Mystery of the Night", author="Agatha Christie", year=1980, genre="Mystery", copies=5, available_copies=1, is_loaned="Yes"),
        4: Book(title="The Science of Everything", author="Isaac Newton", year=1687, genre="Science", copies=3, available_copies=3, is_loaned="No"),
        5: Book(title="A Tale of Two Cities", author="Charles Dickens", year=1859, genre="Fiction", copies=7, available_copies=0, is_loaned="Yes"),
    }

# טסטים לאסטרטגיות חיפוש

def test_title_search(sample_books):
    strategy = TitleSearchStrategy()

    # בדיקה למציאת ספר קיים לפי הכותרת
    results = strategy.search("Python", sample_books)
    assert len(results) == 1
    assert results[0].title == "Python Programming"

    # בדיקה לחיפוש שלא מחזיר תוצאה
    results = strategy.search("Nonexistent", sample_books)
    assert len(results) == 0

    # חיפוש עם רגישות למקרים שונים (Case Insensitivity)
    results = strategy.search("pYtHoN", sample_books)
    assert len(results) == 1


def test_author_search(sample_books):
    strategy = AuthorSearchStrategy()

    # בדיקה למציאת ספר לפי שם המחבר
    results = strategy.search("John", sample_books)
    assert len(results) == 1
    assert results[0].author == "John Smith"

    # חיפוש לפי שם מחבר שלא קיים
    results = strategy.search("Unknown Author", sample_books)
    assert len(results) == 0

    # חיפוש חלקי של שם
    results = strategy.search("Doe", sample_books)
    assert len(results) == 1
    assert results[0].author == "Jane Doe"


def test_genre_search(sample_books):
    strategy = GenreSearchStrategy()

    # בדיקה למציאת ספר לפי ז'אנר
    results = strategy.search("Education", sample_books)
    assert len(results) == 2

    # חיפוש בז'אנר שלא קיים
    results = strategy.search("Fantasy", sample_books)
    assert len(results) == 0

    # חיפוש עם רגישות למקרים שונים (Case Insensitivity)
    results = strategy.search("mYsTeRy", sample_books)
    assert len(results) == 1
    assert results[0].genre == "Mystery"


def test_year_search(sample_books):
    strategy = YearSearchStrategy()

    # בדיקה למציאת ספר לפי שנה מדויקת
    results = strategy.search("2020", sample_books)
    assert len(results) == 1
    assert results[0].year == 2020

    # חיפוש שנה שלא קיימת
    results = strategy.search("1900", sample_books)
    assert len(results) == 0

    # חיפוש שנה חלקית (לדוגמה "20")
    results = strategy.search("20", sample_books)
    assert len(results) == 2
    assert any(book.year == 2020 for book in results)
    assert any(book.year == 2019 for book in results)

    # חיפוש שנה חלקית שאינה תואמת (לדוגמה "19" עם התאמות לא רלוונטיות)
    results = strategy.search("19", sample_books)
    assert len(results) == 2
    assert any(book.year == 2019 for book in results)
    assert any(book.year == 1980 for book in results)



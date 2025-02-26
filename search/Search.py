from Models.BookIterator import AllBooksIterator, AvailableBooksIterator, LoanedBooksIterator
from Services.Logger import Logger
from Decorator.Decorator import log_operation


class Search:
    def __init__(self, books: dict, waiting_list=None, books_borrowed=None):
        """
        אתחול מחלקת החיפוש

        Args:
            books (dict): מילון של כל הספרים
            waiting_list (dict, optional): מילון של רשימות המתנה לכל ספר
            books_borrowed (dict, optional): מילון של כמות העותקים המושאלים לכל ספר
        """
        self.books = books
        self.waiting_list = waiting_list if waiting_list is not None else {}
        self.books_borrowed = books_borrowed if books_borrowed is not None else {}
        self.strategy = None
        log_file_path = Logger.get_dynamic_path("Files/Log")
        self.logger = Logger(log_file_path).get_logger()
    def __iter__(self):
        return AllBooksIterator(self.books, self.logger)

    def get_available_iterator(self):
        return AvailableBooksIterator(self.books, self.logger)

    def get_borrowed_iterator(self):
        return LoanedBooksIterator(self.books_borrowed, self.logger)

    def set_strategy(self, strategy):
        """קובע את אסטרטגיית החיפוש."""
        self.strategy = strategy

    def search(self, query: str):
        if not self.strategy:
            raise ValueError("No search strategy set.")
        return self.strategy.search(query, self.books)

    @log_operation("Display all books")
    def display_all_books(self):
        books = []
        iterator = self.__iter__()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    @log_operation("Display available books")
    def display_available_books(self):
        books = []
        iterator = self.get_available_iterator()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    @log_operation("Display borrowed books")
    def display_borrowed_books(self):
        books = []
        iterator = self.get_borrowed_iterator()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    @log_operation("Display books by category")
    def display_books_by_genre(self, genre: str):
        books = []
        for book in self.books.values():
            if book.genre.lower() == genre.lower():
                books.append(book)
        return books


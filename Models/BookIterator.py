from abc import ABC, abstractmethod


class BookIterator(ABC):
    @abstractmethod
    def has_next(self):
        pass

    @abstractmethod
    def next(self):
        pass


# מימושים ספציפיים של Iterator
class AllBooksIterator(BookIterator):

    def __init__(self, books,logger):
        self.books = list(books.values())
        self.index = 0
        self.logger = logger

    def has_next(self):
        return self.index < len(self.books)

    def next(self):
        if self.has_next():
            book = self.books[self.index]
            self.index += 1
            return book
        self.logger.error("Displayed all books fail")
        raise StopIteration()


class AvailableBooksIterator(BookIterator):
    def __init__(self, books,logger):
        self.books = [book for book in books.values() if book.available_copies > 0]
        self.index = 0
        self.logger = logger

    def has_next(self):
        return self.index < len(self.books)

    def next(self):
        if self.has_next():
            book = self.books[self.index]
            self.index += 1
            return book
        self.logger.error("Displayed available books fail")
        raise StopIteration()


class LoanedBooksIterator(BookIterator):
    def __init__(self, books,logger):

        self.books = [book for book in books.values() if book.copies > book.available_copies]

        self.index = 0
        self.logger = logger

    def has_next(self):
        return self.index < len(self.books)

    def next(self):
        if self.has_next():
            book = self.books[self.index]
            self.index += 1
            return book
        self.logger.error("Displayed borrowed books fail")
        raise StopIteration()
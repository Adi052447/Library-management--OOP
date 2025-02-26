from abc import ABC, abstractmethod
from Decorator.Decorator import log_operation
from Services.Logger import Logger


# מחלקת בסיס לאסטרטגיות
class SearchStrategy(ABC):
    @abstractmethod
    def search(self, query: str, books: dict):
        pass

import logging

class TitleSearchStrategy(SearchStrategy):
    def __init__(self):
        super().__init__()
        log_file_path = Logger.get_dynamic_path("Files/Log")
        self.logger = Logger(log_file_path).get_logger()
    def search(self, query: str, books: dict):
        query_lower = query.lower()
        results = [book for book in books.values() if str(query_lower) in str(book.title.lower())]

        if results:
            self.logger.info(f"Search book '{query}' by name completed successfully")
        else:
            self.logger.error(f"Search book '{query}' by name completed fail")

        return results

class AuthorSearchStrategy(SearchStrategy):
    def __init__(self):
        super().__init__()
        log_file_path = Logger.get_dynamic_path("Files/Log")
        self.logger = Logger(log_file_path).get_logger()
    def search(self, query: str, books: dict):
        query_lower = query.lower()
        results = [book for book in books.values() if query_lower in book.author.lower()]

        if results:
            self.logger.info(f"Search book '{query}' by author completed successfully")
        else:
            self.logger.error(f"Search book '{query}' by author completed fail")

        return results


class GenreSearchStrategy(SearchStrategy):
    def __init__(self):
        super().__init__()
        log_file_path = Logger.get_dynamic_path("Files/Log")
        self.logger = Logger(log_file_path).get_logger()
    def search(self, query: str, books: dict):
        query_lower = query.lower()
        results = [book for book in books.values() if query_lower in book.genre.lower()]

        if results:
            self.logger.info(f"Search book '{query}' by genre completed successfully")
        else:
            self.logger.error(f"Search book '{query}' by genre completed fail")

        return results


class YearSearchStrategy(SearchStrategy):

    def __init__(self):
        super().__init__()
        log_file_path = Logger.get_dynamic_path("Files/Log")
        self.logger = Logger(log_file_path).get_logger()
    def search(self, query: str, books: dict):
        results = [book for book in books.values() if query in str(book.year)]

        if results:
            self.logger.info(f"Search book '{query}' by year completed successfully")
        else:
            self.logger.error(f"Search book '{query}' by year completed fail")

        return results

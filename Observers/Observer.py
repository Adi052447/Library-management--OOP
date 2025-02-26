from abc import ABC, abstractmethod
from typing import List

from Models.Book import Book
from Models.Customer import Customer


class Observer(ABC):
    @abstractmethod
    def update(self, book: Book, customers: List[Customer], event_type: str):
        pass
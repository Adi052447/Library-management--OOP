from abc import ABC, abstractmethod
from typing import List

from Models.Book import Book
from Models.Customer import Customer
from Observers.Observer import Observer


class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer):
        pass

    @abstractmethod
    def detach(self, observer: Observer):
        pass

    @abstractmethod
    def notify(self, book: Book, customers: List[Customer], event_type: str):
        pass

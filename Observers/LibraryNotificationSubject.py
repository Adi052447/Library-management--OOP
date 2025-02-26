from typing import List
from Models.Book import Book
from Models.Customer import Customer
from Observers.Observer import Observer
from Observers.Subject import Subject


class LibraryNotificationSubject(Subject):
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, book: Book, customers: List[Customer], event_type: str):
        for observer in self._observers:
            observer.update(book, customers, event_type)

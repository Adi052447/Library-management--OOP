class BookExistsException(Exception):
    def __init__(self, message="The book already exists in the library."):
        super().__init__(message)

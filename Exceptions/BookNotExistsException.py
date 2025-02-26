class BookNotExistsException(Exception):
    """Exception raised for invalid year."""

    def __init__(self, message="Book does not exist, cannot be removed."):
        self.message = message
        super().__init__(self.message)
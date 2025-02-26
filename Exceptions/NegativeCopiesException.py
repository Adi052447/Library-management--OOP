

class NegativeCopiesException(Exception):
    """Exception raised for negative copy count."""

    def __init__(self, message="Total copies cannot be negative or zero."):
        self.message = message
        super().__init__(self.message)
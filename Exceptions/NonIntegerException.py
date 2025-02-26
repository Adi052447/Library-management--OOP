
class NonIntegerException(Exception):
    """Exception raised for non-integer year or copies."""
    def __init__(self, message="Year or copies must be an Integer."):
        self.message = message
        super().__init__(self.message)
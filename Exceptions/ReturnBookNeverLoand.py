class ReturnBookNeverLoand(Exception):
    """Exception raised for negative copy count."""

    def __init__(self, message="you can't return book that never lend"):
        self.message = message
        super().__init__(self.message)
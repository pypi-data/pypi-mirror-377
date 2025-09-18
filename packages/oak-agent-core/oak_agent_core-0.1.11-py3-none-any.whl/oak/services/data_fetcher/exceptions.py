class DatabaseConnectionError(Exception):
    """
    Custom exception raised for database connection failures.
    """
    def __init__(self, message="A database connection error occurred."):
        self.message = message
        super().__init__(self.message)
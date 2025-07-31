class CellError(Exception):
    """Cell activity malfunction"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

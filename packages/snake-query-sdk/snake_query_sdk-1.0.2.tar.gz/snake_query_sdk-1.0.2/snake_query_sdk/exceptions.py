class SnakeQueryError(Exception):
    """Base exception for SnakeQuery SDK errors."""
    def __init__(self, message, status=None, response=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.response = response

    def __str__(self):
        if self.status:
            return f'[Status: {self.status}] {self.message}'
        return self.message

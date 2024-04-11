class TaskResult:
    def __init__(self, success: bool, message: str = None, data: dict = None):
        self.success = success
        self.message = message
        self.data = data if data is not None else {}

    def __str__(self):
        return f"Success: {self.success}, Message: {self.message}, Data: {self.data}"

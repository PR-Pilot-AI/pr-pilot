class TaskContext:
    """Represents the context in which the task is run."""

    def __init__(self, task):
        self.task = task

    def acknowledge_user_prompt(self):
        """Acknowledge the user's prompt so they know we've received their request."""
        pass

    def respond_to_user(self, message):
        """
        Respond to the user's request once the task is finished.
        :param message: The message to send to the user
        """
        pass

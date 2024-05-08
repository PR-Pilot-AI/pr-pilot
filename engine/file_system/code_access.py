from functools import wraps


def needs_code_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Placeholder for cloning logic
        print("Cloning repository...")
        return func(*args, **kwargs)
    return wrapper

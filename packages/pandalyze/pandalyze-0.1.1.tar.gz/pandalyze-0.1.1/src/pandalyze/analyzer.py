import time
from functools import wraps

def analyze(func):
    """
    Decorator to profile execution time of a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        runtime = end - start
        print(f"[pandalyze] {func.__name__} took {runtime:.4f} seconds")
        return result
    return wrapper

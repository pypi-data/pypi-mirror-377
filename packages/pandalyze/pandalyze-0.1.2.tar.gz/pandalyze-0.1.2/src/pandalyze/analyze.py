from pandalyze.profiler import Profiler

def analyze(func):
    """
    Decorator to run a function with profiling enabled.
    Patches pandas operations defined in the config.
    """
    def wrapper(*args, **kwargs):
        profiler = Profiler()
        profiler.patch()

        result = func(*args, **kwargs)

        profiler.report()
        return result
    return wrapper

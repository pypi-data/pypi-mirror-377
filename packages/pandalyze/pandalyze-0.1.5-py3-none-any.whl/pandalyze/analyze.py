from time import perf_counter
from .profiler import Profiler

profiler = Profiler()

def analyze(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        profiler.patch()
        result = func(*args, **kwargs)
        end = perf_counter()
        profiler.overall_time = end - start
        profiler.report()
        return result
    return wrapper

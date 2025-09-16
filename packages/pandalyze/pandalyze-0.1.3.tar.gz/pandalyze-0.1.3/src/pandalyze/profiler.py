import time
from functools import wraps
import pandas as pd
from pandalyze.config.operation_targets_config import DEFAULT_TARGETS

class Profiler:
    def __init__(self, operation_targets=DEFAULT_TARGETS):
        self.operation_targets = operation_targets
        self.stats = {}

    def _wrap_function(self, category: str, func_name: str, func):
        """Wrap a function or method to record its runtime."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start

            self.stats.setdefault(category, {}).setdefault(func_name, []).append(duration)
            return result
        return wrapper

    def patch(self):
        """Patch pandas top-level functions and DataFrame methods."""
        for category, funcs in self.operation_targets.targets.items():
            if category == "pandas":
                # Patch top-level pandas functions (e.g., read_csv, read_excel)
                for func_name in funcs:
                    if hasattr(pd, func_name):
                        original = getattr(pd, func_name)
                        wrapped = self._wrap_function(category, func_name, original)
                        setattr(pd, func_name, wrapped)

            elif category == "DataFrame":
                # Patch DataFrame instance methods (e.g., groupby, merge, apply)
                for method_name in funcs:
                    if hasattr(pd.DataFrame, method_name):
                        original = getattr(pd.DataFrame, method_name)
                        wrapped = self._wrap_function(category, method_name, original)
                        setattr(pd.DataFrame, method_name, wrapped)

    def report(self):
        """Print a profiling summary."""
        print("=== Pandalyze Profiling Report ===")
        total_time = 0.0
        for category, funcs in self.stats.items():
            print(f"\n[{category}]")
            for func_name, times in funcs.items():
                count = len(times)
                avg = sum(times) / count
                total = sum(times)
                total_time += total
                print(f"  {func_name}: {count} calls | avg {avg:.6f}s | total {total:.6f}s")
        print(f"\nOverall runtime tracked: {total_time:.6f}s")

from time import perf_counter
from rich.console import Console
from rich.table import Table
import pandas as pd
from .models.operation_targets import OperationTargets
from .config.operation_targets_config import DEFAULT_TARGETS

class Profiler:
    def __init__(self, targets: OperationTargets = DEFAULT_TARGETS):
        self.targets = targets.targets  # dict[str, list[str]]
        self.stats = {category: {} for category in self.targets}
        self.overall_time = 0.0
        self.console = Console()

    def track_call(self, category: str, operation: str, duration: float):
        if operation not in self.stats[category]:
            self.stats[category][operation] = {"calls": 0, "total": 0.0, "avg": 0.0}
        stat = self.stats[category][operation]
        stat["calls"] += 1
        stat["total"] += duration
        stat["avg"] = stat["total"] / stat["calls"]

    def patch(self):
        # Patch pandas-level functions
        for func_name in self.targets.get("pandas", []):
            if hasattr(pd, func_name):
                original = getattr(pd, func_name)

                def wrapper(*args, __orig=original, __name=func_name, **kwargs):
                    start = perf_counter()
                    result = __orig(*args, **kwargs)
                    end = perf_counter()
                    self.track_call("pandas", __name, end - start)
                    return result

                setattr(pd, func_name, wrapper)

        # Patch DataFrame methods
        for method_name in self.targets.get("DataFrame", []):
            if hasattr(pd.DataFrame, method_name):
                original = getattr(pd.DataFrame, method_name)

                def wrapper(df_self, *args, __orig=original, __name=method_name, **kwargs):
                    start = perf_counter()
                    result = __orig(df_self, *args, **kwargs)
                    end = perf_counter()
                    self.track_call("DataFrame", __name, end - start)
                    return result

                setattr(pd.DataFrame, method_name, wrapper)

    def report(self):
        self.console.print("[bold underline]=== Pandalyze Profiling Report ===[/bold underline]\n")

        for category, operations in self.stats.items():
            if not operations:
                continue
            table = Table(title=f"[cyan]{category}[/cyan]", show_lines=True)
            table.add_column("Operation", justify="left")
            table.add_column("Calls", justify="right")
            table.add_column("Avg Time (s)", justify="right")
            table.add_column("Total Time (s)", justify="right")

            for op, stat in operations.items():
                table.add_row(
                    op,
                    str(stat["calls"]),
                    f"{stat['avg']:.6f}",
                    f"{stat['total']:.6f}"
                )

            self.console.print(table)

        self.console.print(f"[bold green]Overall runtime tracked:[/bold green] {self.overall_time:.6f}s\n")

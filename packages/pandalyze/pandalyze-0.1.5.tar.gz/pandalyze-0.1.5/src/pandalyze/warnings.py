import warnings
from rich.console import Console

console = Console()

class PandalyzeWarning(Warning):
    """Custom warning type for Pandalyze warnings"""
    pass

def warn(message: str, stacklevel=2):
    """Emit a Pandalyze-specific warning."""
    frame_info = ""
    try:
        import inspect
        frame = inspect.stack()[stacklevel]
        frame_info = f"{frame.filename}:{frame.lineno}"
    except Exception:
        pass

    console.print(f"[bold yellow][PandalyzeWarning][/bold yellow] {frame_info}: {message}", style="yellow")

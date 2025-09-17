from dataclasses import dataclass
from typing import Callable

@dataclass
class AntiPatternRule:
    name: str
    description: str
    check: Callable

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class OperationTargets:
    """
    A container for mapping categories (e.g. pandas, DataFrame)
    to the operations we want to track.
    """
    targets: Dict[str, List[str]]
import functools
import pandas as pd
from pandalyze.rules.anti_pattern_rules import DEFAULT_RULES
from .warnings import warn

class AntiPatternDetector:
    def __init__(self, rules=None):
        self.rules = rules or DEFAULT_RULES

    def patch(self):
        for target_class, rules in self.rules.items():
            cls = getattr(pd, target_class)
            for rule in rules:
                if hasattr(cls, rule.name):
                    self._wrap(cls, rule)

    def _wrap(self, cls, rule):
        original = getattr(cls, rule.name)

        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            if rule.check(original, *args, **kwargs):
                warn(f"⚠️ Anti-pattern detected: {rule.description}", stacklevel=2)
            return original(*args, **kwargs)

        setattr(cls, rule.name, wrapper)

def detectantipatterns(func):
    detector = AntiPatternDetector()
    detector.patch()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

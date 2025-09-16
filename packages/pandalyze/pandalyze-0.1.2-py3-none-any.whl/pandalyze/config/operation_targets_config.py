from pandalyze.models.operation_targets import OperationTargets

DEFAULT_TARGETS = OperationTargets(
    targets={
        "pandas": ["read_csv", "read_excel"],
        "DataFrame": ["groupby", "merge", "apply", "concat"]
    }
)
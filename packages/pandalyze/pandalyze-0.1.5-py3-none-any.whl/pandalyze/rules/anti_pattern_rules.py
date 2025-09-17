from pandalyze.models.anti_pattern_model import AntiPatternRule

def _check_apply(df_method, *args, **kwargs):
    func = args[0] if args else kwargs.get("func")
    axis = kwargs.get("axis", None)
    # Trigger if apply is axis=1
    if df_method.__name__ == "apply" and axis == 1:
        return True
    # Trigger if apply(axis=1) and using a lambda function
    if df_method.__name__ == "apply" and axis == 1 and callable(func) and func.__name__ == "<lambda>":
        return True
    return False

def _check_iterrows(df_method, *args, **kwargs):
    return df_method.__name__ == "iterrows"

DEFAULT_RULES = {
    "DataFrame": [
        AntiPatternRule(
            name="apply",
            description="Using DataFrame.apply(axis=1) is inefficient. Prefer vectorization.",
            check=_check_apply
        ),
        AntiPatternRule(
            name="iterrows",
            description="Using DataFrame.iterrows() is slow. Prefer vectorization or itertuples().",
            check=_check_iterrows
        ),
    ]
}

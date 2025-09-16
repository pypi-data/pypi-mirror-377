from pyspark.sql import functions as F, DataFrame

def apply_filters(df: DataFrame, filters: list) -> DataFrame:
    """
    Apply a list of filter definitions to a Spark DataFrame.
    """
    for flt in filters:
        col_expr = F.col(flt["column"])
        val = flt["value"]

        if isinstance(val, str) and flt.get("case_insensitive", False):
            col_expr = F.upper(col_expr)
            val = val.upper()

        op = flt["operator"].upper()
        if op == "=":
            condition = col_expr == val
        elif op == "!=":
            condition = col_expr != val
        elif op == "IN":
            condition = col_expr.isin(val)
        elif op in [">", ">=", "<", "<="]:
            condition = eval(f"col_expr {op} val")
        else:
            raise ValueError(f"Unsupported operator: {op}")

        if flt.get("allow_null", False):
            condition = condition | col_expr.isNull()

        df = df.filter(condition)

    return df


def apply_derived_columns(df: DataFrame, derived_columns: list) -> DataFrame:
    """
    Add derived columns to the DataFrame.
    """
    for col_def in derived_columns:
        expr = col_def["expression"]
        try:
            df = df.withColumn(col_def["name"], F.expr(expr))
        except Exception:
            df = df.withColumn(col_def["name"], F.lit(expr))
    return df
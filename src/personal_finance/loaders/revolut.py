import polars as pl

# Raw Revolut export header -> tidy snake_case column name.
_COLUMN_RENAMES = {
    "Type": "type",
    "Product": "product",
    "Started Date": "started_date",
    "Completed Date": "completed_date",
    "Description": "description",
    "Amount": "amount",
    "Fee": "fee",
    "Currency": "currency",
    "State": "state",
    "Balance": "balance",
}

_DATETIME_COLUMNS = ["started_date", "completed_date"]


def load_revolut(path: str) -> pl.DataFrame:
    """Load a raw Revolut export CSV and coerce it to proper types.

    Amounts already infer as floats; the only coercion needed is parsing the two
    timestamp columns. ``completed_date`` is empty for reverted/pending rows and
    becomes null.
    """
    df = pl.read_csv(path).rename(_COLUMN_RENAMES)

    return df.with_columns(
        pl.col(_DATETIME_COLUMNS).str.to_datetime("%Y-%m-%d %H:%M:%S"),
    )

import polars as pl

# Raw AIB export header -> tidy snake_case column name. Note the leading spaces:
# every column except the first and `Balance` is preceded by a space in the CSV.
_COLUMN_RENAMES = {
    "Posted Account": "account_number",
    " Posted Transactions Date": "transaction_date",
    " Description1": "description_1",
    " Description2": "description_2",
    " Description3": "description_3",
    " Debit Amount": "debit_amount",
    " Credit Amount": "credit_amount",
    "Balance": "balance",
    "Posted Currency": "currency",
    "Transaction Type": "transaction_type",
    "Local Currency Amount": "local_currency_amount",
    "Local Currency": "local_currency",
}

_AMOUNT_COLUMNS = ["debit_amount", "credit_amount", "balance", "local_currency_amount"]


def load_aib(path: str) -> pl.DataFrame:
    """Load a raw AIB export CSV and coerce it to proper types.

    The file is read with everything as strings first, because polars otherwise
    infers the amount columns as floats and then chokes on thousands separators
    (e.g. ``"2,500.00"``) further down the file.
    """
    df = pl.read_csv(path, infer_schema_length=0).rename(_COLUMN_RENAMES)

    return df.with_columns(
        pl.col("transaction_date").str.to_date("%d/%m/%Y"),
        # strip whitespace + thousands separators, treat "" as null, then cast
        pl.col(_AMOUNT_COLUMNS)
        .str.replace_all(",", "")
        .str.strip_chars()
        .replace("", None)
        .cast(pl.Float64),
    )
